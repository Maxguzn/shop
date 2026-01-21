
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

class Device(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    brand = models.CharField(max_length=100, verbose_name="Бренд")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    image = models.ImageField(upload_to='devices/', verbose_name="Изображение")
    
    # Характеристики для сравнения
    screen_size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Диагональ экрана")
    processor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Процессор")
    ram = models.CharField(max_length=50, blank=True, null=True, verbose_name="Оперативная память")
    storage = models.CharField(max_length=50, blank=True, null=True, verbose_name="Встроенная память")
    battery = models.CharField(max_length=50, blank=True, null=True, verbose_name="Аккумулятор")
    os = models.CharField(max_length=100, blank=True, null=True, verbose_name="Операционная система")
    weight = models.CharField(max_length=50, blank=True, null=True, verbose_name="Вес")
    
    # Дополнительные характеристики (храним как JSON)
    specifications = models.TextField(default='{}', verbose_name="Доп. характеристики")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def get_specifications(self):
        """Получить характеристики в виде словаря"""
        try:
            return json.loads(self.specifications)
        except:
            return {}
    
    def set_specification(self, key, value):
        """Установить характеристику"""
        specs = self.get_specifications()
        specs[key] = value
        self.specifications = json.dumps(specs, ensure_ascii=False)
    
    def get_all_characteristics(self):
        """Получить все характеристики товара"""
        characteristics = {}
        
        # Базовые характеристики
        base_specs = {
            'Бренд': self.brand,
            'Цена': f"{self.price} ₽",
            'Категория': self.category.name if self.category else None,
        }
        
        # Технические характеристики
        tech_specs = {
            'Диагональ экрана': self.screen_size,
            'Процессор': self.processor,
            'Оперативная память': self.ram,
            'Встроенная память': self.storage,
            'Аккумулятор': self.battery,
            'Операционная система': self.os,
            'Вес': self.weight,
        }
        
        # Добавляем только непустые значения
        for key, value in {**base_specs, **tech_specs}.items():
            if value:
                characteristics[key] = value
        
        # Добавляем дополнительные характеристики
        characteristics.update(self.get_specifications())
        
        return characteristics
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Comparison(models.Model):
    MAX_ITEMS = 4  # Максимум товаров для сравнения
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    devices = models.ManyToManyField(Device, verbose_name="Товары")
    session_key = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ключ сессии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def add_device(self, device):
        """Добавить товар в сравнение"""
        if self.devices.count() < self.MAX_ITEMS:
            self.devices.add(device)
            return True
        return False
    
    def remove_device(self, device):
        """Удалить товар из сравнения"""
        self.devices.remove(device)
    
    def clear(self):
        """Очистить сравнение"""
        self.devices.clear()
    
    def get_comparison_table(self):
        devices = list(self.devices.all())
        if not devices:
            return {
                'devices': [],
                'characteristics': [],
                'all_specs': [],
                'count': 0
            }

        all_specs_set = set()
        devices_data = []
        
        for device in devices:
            specs = device.get_all_characteristics()
            all_specs_set.update(specs.keys())
            
            devices_data.append({
                'id': device.id,
                'name': device.name,
                'price': device.price,
                'image': device.image,
                'category': device.category.name if device.category else '',
                'specifications': specs
            })
        
        all_specs = sorted(list(all_specs_set))

        comparison_table = []
        for spec in all_specs:
            row = {'specification': spec, 'values': []}
            for device_data in devices_data:
                value = device_data['specifications'].get(spec, '—')
                row['values'].append(value)
            comparison_table.append(row)
        
        return {
            'devices': devices_data,
            'characteristics': comparison_table,
            'all_specs': all_specs,
            'count': len(devices),
            'max_items': self.MAX_ITEMS,
        }
    
    def is_device_in_comparison(self, device_id):
        """Проверить, есть ли товар в сравнении"""
        return self.devices.filter(id=device_id).exists()
    
    @classmethod
    def get_user_comparison(cls, user=None, session_key=None):
        """Получить объект сравнения для пользователя или сессии"""
        if user and user.is_authenticated:
            comparison, created = cls.objects.get_or_create(user=user)
            return comparison
        elif session_key:
            comparison, created = cls.objects.get_or_create(
                session_key=session_key,
                user__isnull=True
            )
            return comparison
        return None
    
    def __str__(self):
        if self.user:
            return f"Сравнение пользователя {self.user.username}"
        return f"Сравнение сессии {self.session_key}"
    
    class Meta:
        verbose_name = "Сравнение"
        verbose_name_plural = "Сравнения"