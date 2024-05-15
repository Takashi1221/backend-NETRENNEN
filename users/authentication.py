from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        token = request.COOKIES.get('access')
        if token:
            # "Bearer"後のスペース必須
            request.META['HTTP_AUTHORIZATION'] = 'Bearer {}'.format(token)
        else:
            return None
        refresh = request.COOKIES.get('refresh')
        request.META['HTTP_REFRESH_TOKEN'] = refresh
        return super().get_header(request)