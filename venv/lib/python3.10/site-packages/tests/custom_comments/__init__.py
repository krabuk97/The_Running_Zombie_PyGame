from django.urls import reverse

from .models import CustomComment
from .forms import CustomCommentForm

def get_model():
    return CustomComment

def get_form():
    return CustomCommentForm

def get_form_target():
    return reverse("custom_comments.views.custom_submit_comment")

def get_flag_url(c):
    return reverse(
        "custom_comments.views.custom_flag_comment",
        args=(c.id,)
    )

def get_delete_url(c):
    return reverse(
        "custom_comments.views.custom_delete_comment",
        args=(c.id,)
    )

def get_approve_url(c):
    return reverse(
        "custom_comments.views.custom_approve_comment",
        args=(c.id,)
    )
