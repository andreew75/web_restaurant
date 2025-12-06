from django.db import models


class GalleryImage(models.Model):
    title = models.CharField(max_length=200, verbose_name="Image Title", blank=True)
    image = models.ImageField(upload_to="gallery_image/", verbose_name="Image")
    full_image = models.ImageField(upload_to="gallery_image/", verbose_name="Full Image", default='gallery_image/default.jpg')
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    order = models.IntegerField(default=0, verbose_name="Order")

    class Meta:
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title
