from django.shortcuts import render
from .models import Review


def reviews_list(request):
    """Страница со всеми отзывами"""
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')

    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/list.html', context)
