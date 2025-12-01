from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='list'),
    path('tag/<slug:tag_slug>/', views.posts_by_tag, name='posts_by_tag'),
    path('<int:post_id>', views.blog_detail, name='detail'),
]
