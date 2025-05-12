# shop/admin.py
from django.contrib import admin
from .models import Watch, Brand, ContactRequest

@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ['model', 'brand', 'in_stock', 'added_at']
    list_filter = ['brand', 'in_stock']
    search_fields = ['model']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'is_resolved']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_resolved']