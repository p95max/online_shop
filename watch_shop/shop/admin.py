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
    list_display = ['name', 'email', 'message_preview', 'created_at', 'is_resolved']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_resolved']
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['mark_as_resolved']

    def message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    message_preview.short_description = 'Message Preview'

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = 'Mark selected requests as resolved'

    class Media:
        css = {
            'all': ('static/css/custom_admin.css',)
        }