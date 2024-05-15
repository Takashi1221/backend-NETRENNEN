from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CombinedResultsViewSet, RaceResultsViewSet, RaceNumberViewSet, HorseEachResultsiViewSet, results_by_date, submit_passing_order

router = DefaultRouter()
router.register(r'horseresults', CombinedResultsViewSet, basename='horseresults')
router.register(r'horseeachresults', HorseEachResultsiViewSet, basename='horseeachresults')
router.register(r'results', RaceResultsViewSet, basename='raceresults')
router.register(r'racenumber', RaceNumberViewSet, basename='racenumber')

urlpatterns = [
    path('', include(router.urls)),
    path('resultsall/', results_by_date),
    path('passing-order/', submit_passing_order, name='submit-passing-order'),

]