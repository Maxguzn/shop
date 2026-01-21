from django.urls import path
from . import views

app_name = 'comparison'

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('remove/<int:product_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    path('', views.comparison_page, name='comparison_page'),
    path('clear/', views.clear_comparison, name='clear_comparison'),
]