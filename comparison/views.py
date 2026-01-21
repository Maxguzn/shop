# comparison/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from main.models import Product
from .models import Comparison
from main.models import Category


@require_POST
def add_to_comparison(request, product_id):
    """Добавление товара в сравнение (AJAX)"""
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем или создаем объект сравнения
    if request.user.is_authenticated:
        comparison, created = Comparison.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        comparison, created = Comparison.objects.get_or_create(
            session_key=session_key,
            user__isnull=True,
            defaults={'session_key': session_key}
        )
    
    # Проверяем, не добавлен ли уже товар
    if comparison.products.filter(id=product.id).exists():
        return JsonResponse({
            'status': 'error',
            'message': f'"{product.name}" уже в сравнении',
            'count': comparison.products.count()
        })
    
    # Проверяем лимит
    if comparison.products.count() >= Comparison.MAX_ITEMS:
        return JsonResponse({
            'status': 'error',
            'message': f'Максимум {Comparison.MAX_ITEMS} товаров в сравнении',
            'count': comparison.products.count()
        })
    
    # Добавляем товар
    comparison.products.add(product)
    
    return JsonResponse({
        'status': 'success',
        'message': f'"{product.name}" добавлен в сравнение',
        'count': comparison.products.count()
    })

def clear_comparison(request):
    """Очистка всего сравнения"""
    if request.user.is_authenticated:
        comparison = Comparison.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        comparison = Comparison.objects.filter(
            session_key=session_key,
            user__isnull=True
        ).first()
    
    if comparison:
        comparison.delete()
        messages.success(request, "Сравнение очищено")
    
    return redirect('comparison:comparison_page')

@require_POST
def remove_from_comparison(request, product_id):
    """Удаление товара из сравнения (AJAX)"""
    product = get_object_or_404(Product, id=product_id)
    
    # Находим объект сравнения
    if request.user.is_authenticated:
        comparison = Comparison.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        comparison = Comparison.objects.filter(
            session_key=session_key,
            user__isnull=True
        ).first()
    
    if comparison:
        comparison.products.remove(product)
        # Если товаров не осталось, можно удалить объект сравнения
        if comparison.products.count() == 0:
            comparison.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'"{product.name}" удален из сравнения',
            'count': comparison.products.count() if hasattr(comparison, 'products') else 0
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Товар не найден в сравнении'
    })


def comparison_page(request):
    """Страница сравнения товаров"""
    # Получаем объект сравнения
    if request.user.is_authenticated:
        comparison = Comparison.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        comparison = Comparison.objects.filter(
            session_key=session_key,
            user__isnull=True
        ).first()
    
    table_data = {
        'products': [],
        'characteristics': [],
        'all_specs': [],
        'count': 0,
        'max_items': Comparison.MAX_ITEMS,
    }
    
    if comparison:
        table_data = comparison.get_comparison_table()
    
    categories = Category.objects.all()
    
    context = {
        'title': 'Сравнение товаров',
        'products': table_data['products'],
        'characteristics': table_data['characteristics'],
        'all_specs': table_data['all_specs'],
        'count': table_data['count'],
        'max_items': table_data['max_items'],
        'categories': categories,
        'comparison_count': table_data['count'],
    }
    
    return render(request, 'comparison/comparison_page.html', context)