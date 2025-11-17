from django.shortcuts import render
from .models import MenuItem, Category


# Create your views here.
def menu_list(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'menu/list.html', context)
