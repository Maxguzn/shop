from django.contrib import admin
from .models import Device, Category, Comparison
import json

class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'category', 'created_at']
    list_filter = ['brand', 'category', 'created_at']
    search_fields = ['name', 'brand', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'price', 'description', 'brand', 'category', 'image')
        }),
        ('Технические характеристики', {
            'fields': ('screen_size', 'processor', 'ram', 'storage', 'battery', 'os', 'weight')
        }),
        ('Дополнительные характеристики', {
            'fields': ('specifications',),
            'description': 'В формате JSON: {"Цвет": "Черный", "Материал": "Металл"}'
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def view_specifications(self, obj):
        """Показать характеристики в админке"""
        specs = obj.get_specifications()
        if specs:
            return '<br>'.join([f'<b>{k}:</b> {v}' for k, v in specs.items()])
        return '—'
    view_specifications.allow_tags = True
    view_specifications.short_description = 'Характеристики'

class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'devices_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user(self, obj):
        if obj.user:
            return obj.user.username
        return f'Аноним ({obj.session_key[:10]}...)'
    get_user.short_description = 'Пользователь'
    
    def devices_count(self, obj):
        return obj.devices.count()
    devices_count.short_description = 'Товаров'
    
    def view_devices(self, obj):
        devices = obj.devices.all()
        return ', '.join([d.name for d in devices])
    view_devices.short_description = 'Товары в сравнении'

admin.site.register(Device, DeviceAdmin)
admin.site.register(Category)
admin.site.register(Comparison, ComparisonAdmin)