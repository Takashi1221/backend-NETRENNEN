from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StarterViewSet, RenntermineViewSet, KalenderViewSet, PedigreeViewSet, HorseProfiViewSet, TodayErgebnisViewSet, TodayOddsViewSet

router = DefaultRouter()
router.register(r'renntermine', RenntermineViewSet)
router.register(r'starter', StarterViewSet, basename='starter')
router.register(r'pedigree', PedigreeViewSet, basename='pedigree')
router.register(r'horseprofi', HorseProfiViewSet, basename='horseprofi')
router.register(r'kalender', KalenderViewSet, basename='kalender')
router.register(r'todayergebnis', TodayErgebnisViewSet, basename='todayergebnis')
router.register(r'todayodds', TodayOddsViewSet, basename='todayodds')

urlpatterns = [
    path('', include(router.urls)),

]

