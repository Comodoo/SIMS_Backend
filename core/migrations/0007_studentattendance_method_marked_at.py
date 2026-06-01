from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_enrollment_tokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentattendance',
            name='method',
            field=models.CharField(
                default='manual',
                help_text='How attendance was marked: manual | face | fingerprint',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='studentattendance',
            name='marked_at',
            field=models.DateTimeField(
                auto_now=True,
                help_text='When this record was last updated',
            ),
        ),
    ]
