from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    #path("", admin.site.urls),
    path('api/', include('starter.urls')),
    path('api/', include('results.urls')),
    path('api/', include('users.urls')),
    path('api/', include('news.urls')),
    path('api/', include('payment.urls')),
]
