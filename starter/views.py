from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Starter, Renntermine, KalenderModel, HorsePedigree, HorseProfi, TodayErgebnis, TodayOdds
from .serializers import StarterSerializer, RenntermineSerializer, KalenderSerializer, PedigreeSerializer, HorseProfiSerializer, TodayErgebnisSerializer, TodayOddsSerializer

class StarterViewSet(viewsets.ModelViewSet):
    queryset = Starter.objects.all()
    serializer_class = StarterSerializer
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    
    def get_queryset(self):
        queryset = super().get_queryset()
        race_id = self.request.query_params.get('race_id')
        
        if race_id:
            queryset = queryset.filter(race_id=race_id)
        
        return queryset
    
    
    
class RenntermineViewSet(viewsets.ModelViewSet):
    queryset = Renntermine.objects.all()
    serializer_class = RenntermineSerializer
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    
    def get_queryset(self):
        queryset = super().get_queryset()
        day = self.request.query_params.get('day')
        location = self.request.query_params.get('location')
        
        if day and location:
            queryset = queryset.filter(date=day, location=location)
        
        return queryset
    
    
class KalenderViewSet(viewsets.ModelViewSet):
    queryset = KalenderModel.objects.all()
    serializer_class = KalenderSerializer
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    
class PedigreeViewSet(viewsets.ModelViewSet):
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    serializer_class = PedigreeSerializer
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `horse_id` query parameter in the URL.
        """
        queryset = HorsePedigree.objects.all()
        horse_id = self.request.query_params.get('horse_id')
        if horse_id is not None:
            queryset = queryset.filter(horse_id=horse_id)
        return queryset
    
class HorseProfiViewSet(viewsets.ModelViewSet):
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    serializer_class = HorseProfiSerializer
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `horse_id` query parameter in the URL.
        """
        queryset = HorseProfi.objects.all()
        horse_id = self.request.query_params.get('horse_id')
        if horse_id is not None:
            queryset = queryset.filter(horse_id=horse_id)
        return queryset
    
    
class TodayErgebnisViewSet(viewsets.ModelViewSet):
    queryset = TodayErgebnis.objects.all()
    serializer_class = TodayErgebnisSerializer
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    
    def get_queryset(self):
        queryset = super().get_queryset()
        race_id = self.request.query_params.get('race_id')
        if race_id:
            queryset = queryset.filter(race_id=race_id)
        
        return queryset
    
class TodayOddsViewSet(viewsets.ModelViewSet):
    queryset = TodayOdds.objects.all()
    serializer_class = TodayOddsSerializer
    authentication_classes = []  # 認証を適用しない
    permission_classes = [AllowAny] 
    
    def get_queryset(self):
        queryset = super().get_queryset()
        race_id = self.request.query_params.get('race_id')
        if race_id:
            queryset = queryset.filter(race_id=race_id)
        
        return queryset