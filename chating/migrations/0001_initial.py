# Generated by Django 5.1.2 on 2024-10-20 03:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatingRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf', models.FileField(upload_to='pdfs/')),
                ('ai_model', models.CharField(default='gpt-4o-mini', max_length=30)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ChatingRoom', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Chating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat', models.TextField()),
                ('speaker', models.CharField(max_length=30)),
                ('chatingRoom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Chating', to='chating.chatingroom')),
            ],
        ),
    ]
