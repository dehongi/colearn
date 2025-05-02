from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Discussion, Comment, Reaction, UserActivity
from .forms import (
    DiscussionForm,
    CommentForm,
    ReplyForm,
    ReactionForm,
    DiscussionFilterForm,
    ActivityFilterForm,
)


def discussion_list(request):
    """View for listing discussions with filtering and sorting."""
    discussions = Discussion.objects.select_related("author", "course").all()
    filter_form = DiscussionFilterForm(request.GET)

    if filter_form.is_valid():
        # Apply filters
        if status := filter_form.cleaned_data.get("status"):
            discussions = discussions.filter(status=status)
        if search := filter_form.cleaned_data.get("search"):
            discussions = discussions.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        if filter_form.cleaned_data.get("is_announcement"):
            discussions = discussions.filter(is_announcement=True)
        if filter_form.cleaned_data.get("is_solved"):
            discussions = discussions.filter(comments__is_solution=True).distinct()

        # Apply sorting
        if sort := filter_form.cleaned_data.get("sort"):
            discussions = discussions.order_by(sort)

    # Add comment count annotation
    discussions = discussions.annotate(total_comments=Count("comments", distinct=True))

    # Pagination
    paginator = Paginator(discussions, 10)  # Show 10 discussions per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "discussions": page_obj,
        "filter_form": filter_form,
    }
    return render(request, "social/discussion_list.html", context)


def discussion_detail(request, slug):
    """View for displaying a single discussion and its comments."""
    discussion = get_object_or_404(
        Discussion.objects.select_related("author", "course", "lesson"), slug=slug
    )

    # Track the view count
    discussion.increment_view_count()

    # Log activity if user is authenticated
    if request.user.is_authenticated:
        UserActivity.log_activity(
            user=request.user,
            activity_type=UserActivity.ActivityType.DISCUSSION_VIEWED,
            discussion=discussion,
        )

    # Prefetch related comments with their authors and reactions
    comments = discussion.comments.select_related("author").filter(parent=None)

    # Prefetch replies for each comment
    comments = comments.prefetch_related(
        Prefetch(
            "replies",
            queryset=Comment.objects.select_related("author").order_by("created_at"),
        )
    )

    # Prefetch reactions
    comments = comments.prefetch_related("reactions")

    # Get user's reactions if authenticated
    user_reactions = {}
    if request.user.is_authenticated:
        reactions = Reaction.objects.filter(
            user=request.user, comment__in=comments
        ).values_list("comment_id", "type")
        user_reactions = dict(reactions)

    comment_form = CommentForm()
    reply_form = ReplyForm()

    context = {
        "discussion": discussion,
        "comments": comments,
        "comment_form": comment_form,
        "reply_form": reply_form,
        "user_reactions": user_reactions,
    }
    return render(request, "social/discussion_detail.html", context)


@login_required
def create_discussion(request):
    """View for creating a new discussion."""
    if request.method == "POST":
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.author = request.user
            discussion.save()

            # Create activity record
            UserActivity.log_activity(
                user=request.user,
                activity_type=UserActivity.ActivityType.DISCUSSION_CREATED,
                discussion=discussion,
            )

            messages.success(request, _("Discussion created successfully!"))
            return redirect(discussion.get_absolute_url())
    else:
        form = DiscussionForm()

    context = {"form": form}
    return render(request, "social/discussion_form.html", context)


@login_required
def edit_discussion(request, slug):
    """View for editing an existing discussion."""
    discussion = get_object_or_404(Discussion, slug=slug)

    # Check if user is the author
    if discussion.author != request.user:
        messages.error(request, _("You don't have permission to edit this discussion."))
        return redirect(discussion.get_absolute_url())

    if request.method == "POST":
        form = DiscussionForm(request.POST, instance=discussion)
        if form.is_valid():
            form.save()
            messages.success(request, _("Discussion updated successfully!"))
            return redirect(discussion.get_absolute_url())
    else:
        form = DiscussionForm(instance=discussion)

    context = {"form": form, "discussion": discussion}
    return render(request, "social/discussion_form.html", context)


@login_required
@require_POST
def add_comment(request, slug):
    """View for adding a comment to a discussion."""
    discussion = get_object_or_404(Discussion, slug=slug)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.discussion = discussion
        comment.author = request.user
        comment.save()

        # Create activity record
        UserActivity.log_activity(
            user=request.user,
            activity_type=UserActivity.ActivityType.COMMENT_ADDED,
            discussion=discussion,
            comment=comment,
        )

        messages.success(request, _("Comment added successfully!"))
    else:
        messages.error(request, _("There was an error adding your comment."))

    return redirect(discussion.get_absolute_url())


@login_required
@require_POST
def add_reply(request, comment_id):
    """View for adding a reply to a comment."""
    parent_comment = get_object_or_404(
        Comment.objects.select_related("discussion"), id=comment_id
    )

    form = ReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.discussion = parent_comment.discussion
        reply.author = request.user
        reply.parent = parent_comment
        reply.save()

        # Create activity record
        UserActivity.log_activity(
            user=request.user,
            activity_type=UserActivity.ActivityType.COMMENT_ADDED,
            discussion=parent_comment.discussion,
            comment=reply,
        )

        messages.success(request, _("Reply added successfully!"))
    else:
        messages.error(request, _("There was an error adding your reply."))

    return redirect(parent_comment.discussion.get_absolute_url())


@login_required
@require_POST
def add_reaction(request, comment_id):
    """View for adding a reaction to a comment."""
    comment = get_object_or_404(
        Comment.objects.select_related("discussion"), id=comment_id
    )
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    form = ReactionForm(request.POST)
    if form.is_valid():
        # Delete existing reaction if any
        Reaction.objects.filter(user=request.user, comment=comment).delete()

        # Create new reaction
        reaction = form.save(commit=False)
        reaction.user = request.user
        reaction.comment = comment
        reaction.save()

        # Create activity record
        UserActivity.log_activity(
            user=request.user,
            activity_type=UserActivity.ActivityType.REACTION_ADDED,
            discussion=comment.discussion,
            comment=comment,
        )

        if is_ajax:
            # Get updated reaction counts for the comment
            reaction_counts = {}
            for reaction_type in Reaction.Type.values:
                count = Reaction.objects.filter(
                    comment=comment, type=reaction_type
                ).count()
                reaction_counts[reaction_type] = count

            return JsonResponse(
                {
                    "status": "success",
                    "reaction_counts": reaction_counts,
                    "user_reaction": reaction.type,
                }
            )

        messages.success(request, _("Reaction added successfully!"))
    else:
        if is_ajax:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
        messages.error(request, _("There was an error adding your reaction."))

    return redirect(comment.discussion.get_absolute_url())


@login_required
@require_POST
def mark_solution(request, comment_id):
    """View for marking a comment as the solution."""
    comment = get_object_or_404(
        Comment.objects.select_related("discussion"), id=comment_id
    )
    discussion = comment.discussion

    # Check if user is the discussion author
    if discussion.author != request.user:
        messages.error(request, _("Only the discussion author can mark solutions."))
        return redirect(discussion.get_absolute_url())

    # Use the model method to mark as solution
    comment.mark_as_solution()

    # Create activity record
    UserActivity.log_activity(
        user=request.user,
        activity_type=UserActivity.ActivityType.SOLUTION_MARKED,
        discussion=discussion,
        comment=comment,
    )

    messages.success(request, _("Solution marked successfully!"))
    return redirect(discussion.get_absolute_url())


@login_required
@require_POST
def close_discussion(request, slug):
    """View for closing a discussion."""
    discussion = get_object_or_404(Discussion, slug=slug)

    # Check if user is the author or has permission
    if discussion.author != request.user and not request.user.is_staff:
        messages.error(
            request, _("You don't have permission to close this discussion.")
        )
        return redirect(discussion.get_absolute_url())

    discussion.close()

    # Log activity
    UserActivity.log_activity(
        user=request.user,
        activity_type=UserActivity.ActivityType.DISCUSSION_CLOSED,
        discussion=discussion,
    )

    messages.success(request, _("Discussion closed successfully!"))
    return redirect(discussion.get_absolute_url())


@login_required
@require_POST
def reopen_discussion(request, slug):
    """View for reopening a closed discussion."""
    discussion = get_object_or_404(Discussion, slug=slug)

    # Check if user is the author or has permission
    if discussion.author != request.user and not request.user.is_staff:
        messages.error(
            request, _("You don't have permission to reopen this discussion.")
        )
        return redirect(discussion.get_absolute_url())

    discussion.reopen()

    # Log activity
    UserActivity.log_activity(
        user=request.user,
        activity_type=UserActivity.ActivityType.DISCUSSION_REOPENED,
        discussion=discussion,
    )

    messages.success(request, _("Discussion reopened successfully!"))
    return redirect(discussion.get_absolute_url())


@login_required
def user_activity(request):
    """View for displaying user activity feed."""
    activities = UserActivity.objects.filter(user=request.user).select_related(
        "user", "discussion", "comment"
    )

    # Get the filter form
    filter_form = ActivityFilterForm(request.GET)

    # Apply filters if the form is valid
    if filter_form.is_valid():
        # Filter by activity type
        if activity_type := filter_form.cleaned_data.get("activity_type"):
            activities = activities.filter(activity_type=activity_type)

        # Filter by date range
        if date_from := filter_form.cleaned_data.get("date_from"):
            activities = activities.filter(created_at__gte=date_from)

        if date_to := filter_form.cleaned_data.get("date_to"):
            # Add one day to include the entire end date
            date_to = datetime.combine(date_to, datetime.max.time())
            activities = activities.filter(created_at__lte=date_to)

        # Apply sorting
        if sort := filter_form.cleaned_data.get("sort"):
            activities = activities.order_by(sort)
    else:
        # Default sorting by most recent
        activities = activities.order_by("-created_at")

    # Calculate activity statistics
    total_activities = activities.count()
    activities_today = activities.filter(
        created_at__gte=timezone.now().replace(hour=0, minute=0, second=0)
    ).count()
    activities_this_week = activities.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # Count by activity type
    activity_counts = (
        activities.values("activity_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Pagination
    paginator = Paginator(activities, 20)  # Show 20 activities per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "activities": page_obj,
        "filter_form": filter_form,
        "total_activities": total_activities,
        "activities_today": activities_today,
        "activities_this_week": activities_this_week,
        "activity_counts": activity_counts,
    }
    return render(request, "social/user_activity.html", context)
