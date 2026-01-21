from django import forms
from ..main.models import Product, Comparison

class ComparisonForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.CharField(widget=forms.HiddenInput())  # 'add' или 'remove'
    
    def clean_product_id(self):
        product_id = self.cleaned_data['product_id']
        try:
            Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise forms.ValidationError("Товар не найден")
        return product_id

class AddSpecificationForm(forms.Form):
    key = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Например: Цвет', 'class': 'form-control'})
    )
    value = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Например: Черный', 'class': 'form-control'})
    )