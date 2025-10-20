# Generated migration for notification preferences

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        ('registration', '0003_user_college_name_user_university_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='notification_preferences', to='registration.user')),
                ('enable_sound', models.BooleanField(default=True, help_text='Play sound when receiving messages')),
                ('enable_desktop', models.BooleanField(default=True, help_text='Show desktop notifications')),
                ('enable_email', models.BooleanField(default=False, help_text='Send email notifications')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'chat_notification_preference',
            },
        ),
    ]
