from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import JsonResponse
from .models import Discussion, Comment, Reaction, UserActivity
from .forms import (
    DiscussionForm,
    CommentForm,
    ReplyForm,
    ReactionForm,
    DiscussionFilterForm,
)


def discussion_list(request):
    """View for listing discussions with filtering and sorting."""
    discussions = Discussion.objects.all()
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

    context = {
        "discussions": discussions,
        "filter_form": filter_form,
    }
    return render(request, "social/discussion_list.html", context)


def discussion_detail(request, slug):
    """View for displaying a single discussion and its comments."""
    discussion = get_object_or_404(Discussion, slug=slug)
    comments = discussion.comments.filter(parent=None)  # Get only top-level comments
    comment_form = CommentForm()
    reply_form = ReplyForm()

    context = {
        "discussion": discussion,
        "comments": comments,
        "comment_form": comment_form,
        "reply_form": reply_form,
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
            UserActivity.objects.create(
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
def add_comment(request, slug):
    """View for adding a comment to a discussion."""
    discussion = get_object_or_404(Discussion, slug=slug)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.author = request.user
            comment.save()

            # Create activity record
            UserActivity.objects.create(
                user=request.user,
                activity_type=UserActivity.ActivityType.COMMENT_ADDED,
                discussion=discussion,
                comment=comment,
            )

            messages.success(request, _("Comment added successfully!"))
            return redirect(discussion.get_absolute_url())

    return redirect(discussion.get_absolute_url())


@login_required
def add_reply(request, comment_id):
    """View for adding a reply to a comment."""
    parent_comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.discussion = parent_comment.discussion
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()

            # Create activity record
            UserActivity.objects.create(
                user=request.user,
                activity_type=UserActivity.ActivityType.COMMENT_ADDED,
                discussion=parent_comment.discussion,
                comment=reply,
            )

            messages.success(request, _("Reply added successfully!"))
            return redirect(parent_comment.discussion.get_absolute_url())

    return redirect(parent_comment.discussion.get_absolute_url())


@login_required
def add_reaction(request, comment_id):
    """View for adding a reaction to a comment."""
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
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
            UserActivity.objects.create(
                user=request.user,
                activity_type=UserActivity.ActivityType.REACTION_ADDED,
                discussion=comment.discussion,
                comment=comment,
            )

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})

            messages.success(request, _("Reaction added successfully!"))
            return redirect(comment.discussion.get_absolute_url())

    return redirect(comment.discussion.get_absolute_url())


@login_required
def mark_solution(request, comment_id):
    """View for marking a comment as the solution."""
    comment = get_object_or_404(Comment, id=comment_id)
    discussion = comment.discussion

    # Check if user is the discussion author
    if discussion.author != request.user:
        messages.error(request, _("Only the discussion author can mark solutions."))
        return redirect(discussion.get_absolute_url())

    # Unmark any existing solution
    Comment.objects.filter(discussion=discussion, is_solution=True).update(
        is_solution=False
    )

    # Mark this comment as solution
    comment.is_solution = True
    comment.save()

    # Create activity record
    UserActivity.objects.create(
        user=request.user,
        activity_type=UserActivity.ActivityType.SOLUTION_MARKED,
        discussion=discussion,
        comment=comment,
    )

    messages.success(request, _("Solution marked successfully!"))
    return redirect(discussion.get_absolute_url())


@login_required
def user_activity(request):
    """View for displaying user activity feed."""
    activities = UserActivity.objects.filter(user=request.user)
    context = {"activities": activities}
    return render(request, "social/user_activity.html", context)
