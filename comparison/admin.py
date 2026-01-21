from django.contrib import admin
from .models import Product, Category, Comparison
import json

class ProductAdmin(admin.ModelAdmin):
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
        specs = obj.get_specifications()
        if specs:
            return '<br>'.join([f'<b>{k}:</b> {v}' for k, v in specs.items()])
        return '—'
    view_specifications.allow_tags = True

class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'products_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user(self, obj):
        if obj.user:
            return obj.user.username
        return f'Anonim ({obj.session_key[:10]}...)'
    get_user.short_description = 'User'
    
    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Products'
    
    def view_products(self, obj):
        products = obj.products.all()
        return ', '.join([d.name for d in products])
    view_products.short_description = 'Products in comparison.'

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Comparison, ComparisonAdmin)