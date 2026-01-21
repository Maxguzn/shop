
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
import json

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    brand = models.CharField(max_length=100, verbose_name="Бренд")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def get_specifications(self):
        try:
            return json.loads(self.specifications)
        except:
            return {}
    
    def set_specification(self, key, value):
        specs = self.get_specifications()
        specs[key] = value
        self.specifications = json.dumps(specs, ensure_ascii=False)
    
    def get_all_characteristics(self):
        characteristics = {}
        base_specs = {
            'Бренд': self.brand,
            'Цена': f"{self.price} ₽",
            'Категория': self.category.name if self.category else None,
        }
        
        for key, value in {**base_specs}.items():
            if value:
                characteristics[key] = value
        characteristics.update(self.get_specifications())
        
        return characteristics
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Comparison(models.Model):
    MAX_ITEMS = 5
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    products = models.ManyToManyField('main.Product', related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'session_key']]
        verbose_name = 'Comparison'
        verbose_name_plural = 'Comparison'
    
    def __str__(self):
        if self.user:
            return f"Comparison user {self.user}"
        return f"Comparison session {self.session_key}"
    
    def get_comparison_table(self):
        products = list(self.products.all())
        if not products:
            return {
                'products': [],
                'characteristics': [],
                'all_specs': [],
                'count': 0,
                'max_items': self.MAX_ITEMS,
            }

        all_specs_set = set()
        products_data = []

        for product in products:
            specs = {}
            if hasattr(product, 'get_all_characteristics'):
                specs = product.get_all_characteristics()
            
            all_specs_set.update(specs.keys())

            # Безопасное получение URL изображения
            image_url = ''
            if hasattr(product, 'image') and product.image:
                try:
                    # Проверяем разные варианты
                    if hasattr(product.image, 'url'):
                        # Если это ImageField/FileField
                        image_url = product.image.url  # ← используем .url а не .image_url
                    elif isinstance(product.image, str):
                        # Если это строка с путем
                        image_url = product.image
                    else:
                        # Пробуем получить строковое представление
                        image_url = str(product.image)
                        
                    # Добавляем MEDIA_URL если нужно
                    if image_url and not image_url.startswith(('http://', 'https://', '/')):
                        from django.conf import settings
                        if hasattr(settings, 'MEDIA_URL'):
                            image_url = settings.MEDIA_URL + image_url.lstrip('/')
                except Exception as e:
                    print(f"Error getting image for product {product.id}: {e}")
                    image_url = ''
            else:
                image_url = ''

            products_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug if hasattr(product, 'slug') else '',
                'price': product.price,
                'image': image_url,  # ← передаем полученный URL
                'category': product.category.name if hasattr(product, 'category') and product.category else '',
                'specifications': specs
            })

        all_specs = sorted(list(all_specs_set))

        comparison_table = []
        for spec in all_specs:
            row = {'specification': spec, 'values': []}
            for product_data in products_data:
                value = product_data['specifications'].get(spec, '-')
                row['values'].append(value)
            comparison_table.append(row)

        return {
            'products': products_data,
            'characteristics': comparison_table,
            'all_specs': all_specs,
            'count': len(products),
            'max_items': self.MAX_ITEMS,
        }