from django.db import models
from django.urls import reverse

from .managers import GalleryManager, PublishedGalleryManager
from tango_shared.models import ContentImage, BaseContentModel


class Gallery(BaseContentModel):
    """
    Allows for Gallery creation.
    If you get a "413 Entity Too Large" error when bulk uploading, adjust the Nginx configuration. 

    """
    credit = models.CharField(max_length=200, blank=True)
    published = models.BooleanField(default=True)

    # Managers
    objects = GalleryManager()
    published_objects = PublishedGalleryManager()

    class Meta:
        verbose_name_plural = "galleries"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('gallery_detail', args=[self.slug])

    def get_image(self):
        try:
            return self.galleryimage_set.all()[0]
        except IndexError:
            return None


class GalleryImage(ContentImage):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE
    )
