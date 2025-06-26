from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('base', '0114_optimisedevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='welcome_email_sent',
            field=models.BooleanField(default=False),
        ),
    ] 