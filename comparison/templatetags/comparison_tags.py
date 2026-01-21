from django import template
from ..models import Comparison

register = template.Library()

@register.filter
def is_in_comparison(product, request):
    """Проверяет, находится ли товар в сравнении"""
    if request.user.is_authenticated:
        try:
            comparison = Comparison.objects.get(user=request.user)
            return comparison.devices.filter(id=product.id).exists()
        except Comparison.DoesNotExist:
            return False
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                comparison = Comparison.objects.get(session_key=session_key, user__isnull=True)
                return comparison.devices.filter(id=product.id).exists()
            except Comparison.DoesNotExist:
                return False
    return False