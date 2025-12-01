from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tag name')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='URL tag')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='title')
    content = models.TextField(verbose_name='content')
    short_description = models.TextField(max_length=200, verbose_name='short description')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='author')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='updated')
    image = models.ImageField(upload_to='blog_images/', verbose_name='image')
    is_published = models.BooleanField(default=True, verbose_name='published')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='tags')
    is_best = models.BooleanField(default=False, verbose_name='best post')

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['is_best', '-created_at', 'is_published']),
        ]

    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.id])

    def __str__(self):
        return self.title
