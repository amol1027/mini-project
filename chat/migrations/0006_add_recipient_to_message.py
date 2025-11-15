from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0005_alter_message_message_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="recipient",
            field=models.ForeignKey(
                related_name="received_messages",
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="registration.user",
                help_text="Intended recipient for system messages (optional)",
            ),
        ),
    ]
