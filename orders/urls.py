from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_update, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/update-totals/', views.update_totals, name='update_totals'),
    path('cart/summary/', views.cart_summary, name='cart_summary'),
    # Добавить позже
    path('checkout/', views.checkout, name='checkout'),
    path('verify-sms/', views.verify_sms, name='verify_sms'),
]
