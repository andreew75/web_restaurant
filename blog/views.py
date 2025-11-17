from django.shortcuts import render
from .models import Post, Tag


def blog_list(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    # tags = Tag.objects.all()
    context = {'posts': posts}
    return render(request, 'blog/list.html', context)


def blog_detail(request, post_id):
    ...

    return render(request, 'blog/detail.html')
