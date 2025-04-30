from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    # Discussion URLs
    path("", views.discussion_list, name="discussion_list"),
    path("discussion/create/", views.create_discussion, name="create_discussion"),
    path("discussion/<slug:slug>/", views.discussion_detail, name="discussion_detail"),
    path("discussion/<slug:slug>/edit/", views.edit_discussion, name="edit_discussion"),
    # Comment URLs
    path("discussion/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/reply/", views.add_reply, name="add_reply"),
    path("comment/<int:comment_id>/reaction/", views.add_reaction, name="add_reaction"),
    path(
        "comment/<int:comment_id>/mark-solution/",
        views.mark_solution,
        name="mark_solution",
    ),
    # Activity URL
    path("activity/", views.user_activity, name="user_activity"),
]
