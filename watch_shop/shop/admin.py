# shop/admin.py
from django.contrib import admin
from .models import Watch, Brand, ContactRequest, WatchImage, Order, CartItem, OrderItem


@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ['model', 'brand', 'in_stock', 'added_at', 'views']
    list_filter = ['brand', 'in_stock', 'added_at']
    search_fields = ['model']
    list_editable = ['in_stock']
    prepopulated_fields = {'slug': ('model',)}
    list_per_page = 25
    date_hierarchy = 'added_at'

    # Встраивание WatchImage в форму Watch
    class WatchImageInline(admin.TabularInline):
        model = WatchImage
        extra = 1
        fields = ['image', 'alt_text']

    inlines = [WatchImageInline]

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message_preview', 'created_at', 'is_resolved']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_resolved']
    list_per_page = 25
    date_hierarchy = 'created_at'

    def message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    message_preview.short_description = 'Message Preview'

@admin.register(WatchImage)
class WatchImageAdmin(admin.ModelAdmin):
    list_display = ['watch', 'image', 'alt_text']
    search_fields = ['watch__model', 'alt_text']
    list_filter = ['watch']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['watch', 'quantity', 'session_key', 'total_price']
    search_fields = ['watch__model']
    list_filter = ['session_key']
    list_per_page = 25

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    list_editable = ['status']
    list_per_page = 25
    date_hierarchy = 'created_at'

    class OrderItemInline(admin.TabularInline):
        model = OrderItem
        extra = 0
        fields = ['watch', 'quantity', 'price', 'total_price']
        readonly_fields = ['total_price']

    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'watch', 'quantity', 'price', 'total_price']
    search_fields = ['watch__model']
    list_filter = ['order']
    list_per_page = 25