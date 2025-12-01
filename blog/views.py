from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .forms import SearchForm
from .models import Post, Tag


def blog_list(request):
    # Инициализируем переменные
    posts = Post.objects.filter(is_published=True).select_related('author').prefetch_related('tags').order_by('-created_at')

    query = request.GET.get('q', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(content__icontains=query)
        )

    best_posts = Post.objects.filter(is_published=True, is_best=True).select_related('author').order_by('-created_at')[:3]
    all_tags = Tag.objects.all()
    # Пагинация
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если page не число, показываем первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если page вне диапазона, показываем последнюю страницу
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'best_posts': best_posts,
        'all_tags': all_tags,
        'query': query,
    }
    return render(request, 'blog/list.html', context)


def posts_by_tag(request, tag_slug):
    # Получаем тег по slug или 404
    tag = get_object_or_404(Tag, slug=tag_slug)

    # Получаем поисковый запрос
    query = request.GET.get('q', '')

    # Фильтруем посты по тегу
    posts = Post.objects.filter(
        is_published=True,
        tags=tag
    ).select_related('author').prefetch_related('tags').order_by('-created_at')

    best_posts = Post.objects.filter(
        is_published=True,
        is_best=True
    ).select_related('author').order_by('-created_at')[:3]

    all_tags = Tag.objects.all()

    # Дополнительный фильтр по поиску
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(content__icontains=query)
        )

    paginator = Paginator(posts, 6)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'best_posts': best_posts,
        'all_tags': all_tags,
        'current_tag': tag,  # текущий выбранный тег
        'query': query,
    }
    return render(request, 'blog/list.html', context)


def blog_detail(request, post_id):
    # Получаем пост или 404
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related('tags'),
        id=post_id,
        is_published=True  # показываем только опубликованные
    )

    # Получаем похожие посты (по тегам)
    similar_posts = Post.objects.filter(
        is_published=True,
        tags__in=post.tags.all()
    ).exclude(id=post.id).distinct()[:3]

    # Последние посты для сайдбара
    recent_posts = Post.objects.filter(
        is_published=True
    ).exclude(id=post.id).order_by('-created_at')[:3]

    # Лучшие посты для сайдбара
    best_posts = Post.objects.filter(
        is_published=True,
        is_best=True
    ).exclude(id=post.id).order_by('-created_at')[:3]

    all_tags = Tag.objects.all()

    context = {
        'post': post,
        'similar_posts': similar_posts,
        'recent_posts': recent_posts,
        'best_posts': best_posts,
        'all_tags': all_tags,
    }

    return render(request, 'blog/detail.html', context)

