# Generated by Django 5.0.3 on 2024-06-05 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_customuser_stripe_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='stripe_email',
        ),
        migrations.AddField(
            model_name='customuser',
            name='subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]