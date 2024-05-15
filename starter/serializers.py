from rest_framework import serializers
from .models import Starter, Renntermine, KalenderModel, HorsePedigree, HorseProfi

class StarterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Starter
        fields = '__all__'
        
class RenntermineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Renntermine
        fields = '__all__'
        
class KalenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = KalenderModel
        fields = '__all__'
        
class PedigreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorsePedigree
        fields = '__all__'
        
class HorseProfiSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorseProfi
        fields = '__all__'