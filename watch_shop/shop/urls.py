from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from shop.views import (catalog, item_detail, sort_by_brand)

app_name = 'shop'

urlpatterns = [
    path('', catalog, name='catalog'),
    path('watch/<slug:slug>/', item_detail, name='item_detail'),
    path('sort_by_brand/<slug:slug>/', sort_by_brand, name='sort_by_brand'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
