from .models import Comparison

def comparison_context(request):
    """Добавляет количество товаров в сравнении в контекст"""
    count = 0
    
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
    
    return {
        'comparison_count': count,
        'comparison_max_items': Comparison.MAX_ITEMS,
    }