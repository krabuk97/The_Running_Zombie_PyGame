from django.urls import reverse


def get_model():
    """
    Returns the comment model class.
    """
    from tango_comments.models import Comment
    return Comment


def get_form():
    """
    Returns the comment ModelForm class.
    """
    from tango_comments.forms import CommentForm
    return CommentForm


def get_form_target():
    """
    Returns the target URL for the comment form submission view.
    """
    return reverse("comments-post-comment")


def get_flag_url(comment):
    """
    Get the URL for the "flag this comment" view.
    """
    return reverse("comments-flag", args=(comment.id,))


def get_delete_url(comment):
    """
    Get the URL for the "delete this comment" view.
    """
    return reverse("comments-delete", args=(comment.id,))


def get_approve_url(comment):
    """
    Get the URL for the "approve this comment from moderation" view.
    """
    return reverse("comments-approve", args=(comment.id,))
