from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, post_article


router = DefaultRouter()
router.register(r'get-article', ArticleViewSet, basename='get-article')


urlpatterns = [
    path('', include(router.urls)),
    path('post-article/', post_article, name='post-article'),
]