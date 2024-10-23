# Generated by Django 5.1.1 on 2024-10-14 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VideoPrompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('arrTitles', models.JSONField(blank=True, null=True)),
                ('arrImages', models.JSONField(blank=True, null=True)),
                ('arrVideos', models.JSONField(blank=True, null=True)),
                ('finalVideo', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]