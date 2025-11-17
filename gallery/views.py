from django.shortcuts import render
from .models import GalleryImage


def gallery_list(request):
    images = GalleryImage.objects.all()
    context = {'images': images}
    return render(request, 'gallery/list.html', context)
