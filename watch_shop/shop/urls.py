from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from shop.views import (catalog, item_detail, sort_by_brand, about, contact_us, contact_success)

app_name = 'shop'

urlpatterns = [
    path('', catalog, name='catalog'),
    path('watch/<slug:slug>/', item_detail, name='item_detail'),
    path('sort_by_brand/<slug:slug>/', sort_by_brand, name='sort_by_brand'),
    path('about/', about, name='about'),
    path('contact/', contact_us, name='contact'),
    path('contact_success/', contact_success, name='contact_success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
