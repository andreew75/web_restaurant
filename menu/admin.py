from tkinter import Menu

from django.contrib import admin
from menu.models import MenuItem, Category, MealType


admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(MealType)


