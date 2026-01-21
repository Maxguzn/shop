from django.core.serializers import serializers
from ..main.models import Device, Comparison
from django.contrib.auth.models import User

class DeviceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Device
        fields = [
            'id', 'name', 'price', 'description', 
            'brand', 'category', 'category_name',
            'image', 'image_url',
            'screen_size', 'processor', 'ram', 
            'storage', 'battery', 'operating_system', 'weight'
        ]
        read_only_fields = ['image_url']
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

class ComparisonSerializer(serializers.ModelSerializer):
    devices = DeviceSerializer(many=True, read_only=True)
    devices_count = serializers.SerializerMethodField()
    max_items = serializers.SerializerMethodField()
    comparison_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Comparison
        fields = [
            'id', 'devices', 'devices_count', 'max_items',
            'comparison_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['devices_count', 'comparison_data']
    
    def get_devices_count(self, obj):
        return obj.devices.count()
    
    def get_max_items(self, obj):
        return Comparison.MAX_ITEMS
    
    def get_comparison_data(self, obj):
        return obj.get_comparison_data()

class AddToComparisonSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=True)
    
    def validate_device_id(self, value):
        try:
            Device.objects.get(id=value)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Товар не найден")
        return value