from django.urls import path
from . import views

app_name = 'comparison'

urlpatterns = [
    path('comparison/', views.comparison_page, name='comparison_page'),
    path('comparison/add/<int:device_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('comparison/remove/<int:device_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    path('comparison/clear/', views.clear_comparison, name='clear_comparison'),
    path('comparison/toggle/<int:device_id>/', views.toggle_comparison, name='toggle_comparison'),
]