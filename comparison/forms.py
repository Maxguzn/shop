from django import forms
from ..main.models import Device, Comparison

class ComparisonForm(forms.Form):
    device_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.CharField(widget=forms.HiddenInput())  # 'add' или 'remove'
    
    def clean_device_id(self):
        device_id = self.cleaned_data['device_id']
        try:
            Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise forms.ValidationError("Товар не найден")
        return device_id

class AddSpecificationForm(forms.Form):
    key = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Например: Цвет', 'class': 'form-control'})
    )
    value = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Например: Черный', 'class': 'form-control'})
    )