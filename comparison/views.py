# shop/views.py или main/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Device, Comparison, Category
import json

def comparison_page(request):
    """Главная страница сравнения"""
    # Получаем сравнение для текущего пользователя/сессии
    if request.user.is_authenticated:
        comparison, created = Comparison.objects.get_or_create(user=request.user)
    else:
        # Для анонимных пользователей используем сессию
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        comparison, created = Comparison.objects.get_or_create(
            session_key=session_key,
            user__isnull=True
        )
    
    # Получаем данные для таблицы
    table_data = comparison.get_comparison_table()
    
    # Получаем все категории для меню
    categories = Category.objects.all()
    
    context = {
        'title': 'Product Comparison',
        'devices': table_data['devices'],
        'characteristics': table_data['characteristics'],
        'count': table_data['count'],
        'max_items': Comparison.MAX_ITEMS,
        'categories': categories,
        'comparison_count': comparison.devices.count(),
    }
    
    return render(request, 'comparison/comparison_page.html', context)


def add_to_comparison(request, device_id):
    """Добавить товар в сравнение (через GET запрос)"""
    device = get_object_or_404(Device, id=device_id)
    
    # Получаем или создаем сравнение
    if request.user.is_authenticated:
        comparison, created = Comparison.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        comparison, created = Comparison.objects.get_or_create(
            session_key=session_key,
            user__isnull=True
        )
    
    # Проверяем лимит
    if comparison.devices.count() >= Comparison.MAX_ITEMS:
        messages.error(request, f'You can compare only {Comparison.MAX_ITEMS} products')
    elif comparison.devices.filter(id=device_id).exists():
        messages.info(request, 'Product already in comparison')
    else:
        comparison.devices.add(device)
        messages.success(request, f'"{device.name}" added to comparison')
    
    # Возвращаем на предыдущую страницу
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)

def remove_from_comparison(request, device_id):
    """Удалить товар из сравнения"""
    device = get_object_or_404(Device, id=device_id)
    
    if request.user.is_authenticated:
        comparison = get_object_or_404(Comparison, user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return redirect('comparison_page')
        comparison = get_object_or_404(Comparison, session_key=session_key, user__isnull=True)
    
    if comparison.devices.filter(id=device_id).exists():
        comparison.devices.remove(device)
        messages.success(request, f'"{device.name}" removed from comparison')
    
    return redirect('comparison_page')

def clear_comparison(request):
    """Очистить все сравнение"""
    if request.user.is_authenticated:
        comparison = get_object_or_404(Comparison, user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return redirect('comparison_page')
        comparison = get_object_or_404(Comparison, session_key=session_key, user__isnull=True)
    
    comparison.devices.clear()
    messages.success(request, 'Comparison cleared')
    
    return redirect('comparison_page')

def toggle_comparison(request, device_id):
    """Добавить/удалить товар одной кнопкой"""
    device = get_object_or_404(Device, id=device_id)
    
    # Получаем сравнение
    if request.user.is_authenticated:
        comparison, created = Comparison.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        comparison, created = Comparison.objects.get_or_create(
            session_key=session_key,
            user__isnull=True
        )
    
    # Проверяем, есть ли уже товар
    if comparison.devices.filter(id=device_id).exists():
        # Удаляем
        comparison.devices.remove(device)
        messages.info(request, f'"{device.name}" removed from comparison')
        action = 'removed'
    else:
        # Добавляем
        if comparison.devices.count() >= Comparison.MAX_ITEMS:
            messages.error(request, f'You can compare only {Comparison.MAX_ITEMS} products')
            referer = request.META.get('HTTP_REFERER', '/')
            return redirect(referer)
        
        comparison.devices.add(device)
        messages.success(request, f'"{device.name}" added to comparison')
        action = 'added'
    
    # Возвращаем на предыдущую страницу
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)

# Вьюшка для получения количества товаров в сравнении (для шапки)
def get_comparison_count(request):
    """Получить количество товаров в сравнении (для шапки)"""
    if request.user.is_authenticated:
        try:
            comparison = Comparison.objects.get(user=request.user)
            count = comparison.devices.count()
        except Comparison.DoesNotExist:
            count = 0
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                comparison = Comparison.objects.get(session_key=session_key, user__isnull=True)
                count = comparison.devices.count()
            except Comparison.DoesNotExist:
                count = 0
        else:
            count = 0
    
    return count

# Контекстный процессор для добавления сравнения во все шаблоны
def comparison_context(request):
    """Добавляет счетчик сравнения в контекст всех шаблонов"""
    count = get_comparison_count(request)
    return {
        'comparison_count': count,
        'comparison_max_items': Comparison.MAX_ITEMS,
    }