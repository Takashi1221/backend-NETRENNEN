from django.urls import path, include
from .views import stripe_webhooks


urlpatterns = [
    path('webhook', stripe_webhooks, name='webhook'),
]