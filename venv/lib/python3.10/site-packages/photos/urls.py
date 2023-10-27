from django.urls import path
from django.views.generic import DetailView, ListView

from .models import Gallery

galleries = Gallery.published_objects.all()

urlpatterns = [
    path('', ListView.as_view(queryset=galleries), name="gallery_list"),
    path(
        '<slug:slug>/', 
        DetailView.as_view(
            queryset=galleries,
            template_name="photos/gallery_detail.html"
        ),
        name="gallery_detail"
    ),
]
