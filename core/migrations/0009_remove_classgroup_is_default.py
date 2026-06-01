from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_classgroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classgroup',
            name='is_default',
        ),
    ]
