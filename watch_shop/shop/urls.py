from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from shop.views import (catalog, item_detail, sort_by_brand, about, contact_us,
                        cart_detail, cart_remove, cart_add, order_success, order_create)

app_name = 'shop'

urlpatterns = [
    path('', catalog, name='catalog'),
    path('watch/<slug:slug>/', item_detail, name='item_detail'),
    path('sort_by_brand/<slug:slug>/', sort_by_brand, name='sort_by_brand'),
    path('about/', about, name='about'),
    path('contact/', contact_us, name='contact'),
    path('cart/add/<slug:slug>/', cart_add, name='cart_add'),
    path('cart/remove/<int:cart_item_id>/', cart_remove, name='cart_remove'),
    path('cart/', cart_detail, name='cart_detail'),
    path('order/', order_create, name='order_create'),
    path('order/success/', order_success, name='order_success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
