from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models

# カスタムユーザーモデルを利用するための下記２つの関数を定義
class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    nickname = models.CharField(max_length=50)  # 必須フィールド
    is_subscribed = models.BooleanField(default=False) # True/False
    age_group = models.CharField(max_length=50)  # 必須フィールド  # young/adult/senior
    residence_area = models.CharField(max_length=50)  # 必須フィールド

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'age_group', 'residence_area']  # 必須フィールドリストに追加

    objects = CustomUserManager()