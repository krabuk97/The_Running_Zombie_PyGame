from django.urls import include, path, re_path

from django.contrib.contenttypes.views import shortcut
from django.contrib.auth import views as auth_views

from tango_comments.feeds import LatestCommentFeed

from tests.testapp import views

feeds = {
     'comments': LatestCommentFeed,
}

urlpatterns = [
    path('', include('tango_comments.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('accounts/logout/', auth_views.LogoutView.as_view()),
    path('post/', views.custom_submit_comment),
    re_path(r'^flag/(\d+)/$', views.custom_flag_comment),
    re_path(r'^delete/(\d+)/$', views.custom_delete_comment),
    re_path(r'^approve/(\d+)/$', views.custom_approve_comment),
    re_path(r'^cr/(\d+)/(.+)/$', shortcut, name='comments-url-redirect'),
    path('rss/comments/', LatestCommentFeed , name="comments-feed"),
]
