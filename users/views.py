from django.conf import settings
from rest_framework import generics, status, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .serializers import UserRegistrationSerializer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# SingUp用
class UserRegistrationView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    serializer_class = UserRegistrationSerializer
    # トークンを発行
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token_serializer = TokenObtainPairSerializer(data={
            'email': request.data['email'],
            'password': request.data['password']
        })
        token_serializer.is_valid(raise_exception=True)
        access = token_serializer.validated_data.get("access", None)
        refresh = token_serializer.validated_data.get("refresh", None)
        
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        access_max_age = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        refresh_max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        response.set_cookie('access', access, httponly=True, max_age=access_max_age)
        response.set_cookie('refresh', refresh, httponly=True, max_age=refresh_max_age)
        return response


# ログイン用
class LoginView(APIView):
    # ログイン画面では、認証フリーにする(素のJWTクラス)
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    
    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data.get("access", None)
        refresh = serializer.validated_data.get("refresh", None)
        if access:
            response = Response(status=status.HTTP_200_OK)
            access_max_age = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            refresh_max_age = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            response.set_cookie('access', access, httponly=True, max_age=access_max_age)
            response.set_cookie('refresh', refresh, httponly=True, max_age=refresh_max_age)
            return response
        return Response({'errMsg': 'Benutzerauthentifizierung fehlgeschlagen.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
# トークンのリフレッシュ用
class RefreshView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    
    def post(self, request):
        # refreshの場合はcookieからrefreshトークンを直接取得する
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({'error': 'No refresh token provided.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        # 以下LoginViewと同様
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data.get("access", None)
        if access:
            response = Response(status=status.HTTP_200_OK)
            access_max_age = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            response.set_cookie('access', access, httponly=True, max_age=access_max_age)
            return response
        return Response({'errMsg': 'Benutzerauthentifizierung fehlgeschlagen.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
# ログアウト用
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response
    

# 認証状態の管理
class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ユーザーの認証状態を確認し、結果を返す
        return Response({
            'is_authenticated': request.user.is_authenticated
        })
        

# 課金状態の管理
class UpdateSubscription(APIView):
    # 認証やパーミッションは必要に応じて設定
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            user.is_subscribed = True
            user.save()
            return Response({'success': 'Subscription updated successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# コンタクトからのメール転送
class SendMessageView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request, *args, **kwargs):
        user_email = request.data.get('email')  # ユーザーのメールアドレス
        user_message = request.data.get('message')  # ユーザーが入力したメッセージ
        subject = "Contact Form a User"  # メールの件名

        # メールの作成
        message = Mail(
            from_email='t.mio@netrennen.com',  # 認証済みの送信者アドレス
            to_emails='t.mio@netrennen.com',  # 受信するあなたのメールアドレス
            subject=subject,
            plain_text_content=f"From: {user_email}\nMessage: {user_message}"
        )

        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            return Response({'message': 'Email sent successfully'}, status=response.status_code)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    