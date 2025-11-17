from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tag name')

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

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
