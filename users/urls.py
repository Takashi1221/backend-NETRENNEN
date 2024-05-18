from django.urls import path, include
from .views import UserRegistrationView, LoginView, RefreshView, LogoutView, CheckAuthView, UpdateSubscription, SendMessageView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', UserRegistrationView.as_view(), name='signup'),
    path('login/', LoginView.as_view()),
    path('refresh/', RefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('checkauth/', CheckAuthView.as_view()),
    path('update_subscription/', UpdateSubscription.as_view(), name='update_subscription'),
    path('send-message/', SendMessageView.as_view(), name='send-message'),
]