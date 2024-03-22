# Generated by Django 5.0.2 on 2024-03-06 13:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0005_alter_image_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='total_likes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddIndex(
            model_name='image',
            index=models.Index(fields=['-total_likes'], name='images_imag_total_l_0bcd7e_idx'),
        ),
    ]
