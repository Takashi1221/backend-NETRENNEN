from rest_framework import serializers
from .models import CombinedResults, RaceResults, HorseResults

class CombinedResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombinedResults
        fields = '__all__'
        
        
class RaceResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RaceResults
        fields = '__all__'
        
class RaceNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = RaceResults
        fields = ('this_race_nr', 'race_id') # 必要なフィールドだけ
        
class HorseEachResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorseResults
        fields = '__all__'