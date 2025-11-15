# Migration to alter BorrowOTP.verified_by to point to registration.User
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_uber_style_otp_system'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowotp',
            name='verified_by',
            field=models.ForeignKey(blank=True, help_text='User who verified the OTP', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_otps', to='registration.user'),
        ),
    ]
