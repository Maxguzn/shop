# comparison/templatetags/comparison_tags.py
from django import template
from comparison.models import Comparison

register = template.Library()

@register.filter
def is_in_comparison(product, request):
    if not request:
        return False
    
    try:
        if request.user.is_authenticated:
            comparison = Comparison.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return False
            comparison = Comparison.objects.filter(
                session_key=session_key,
                user__isnull=True
            ).first()
        
        if comparison and product:
            return comparison.products.filter(id=product.id).exists()
        return False
        
    except Exception:
        return False


@register.simple_tag
def get_comparison_count(request):
    if not request:
        return 0
    
    try:
        if request.user.is_authenticated:
            comparison = Comparison.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return 0
            comparison = Comparison.objects.filter(
                session_key=session_key,
                user__isnull=True
            ).first()
        
        if comparison:
            return comparison.products.count()
        
    except Exception:
        return 0