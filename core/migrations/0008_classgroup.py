import uuid
from django.db import migrations, models

DEFAULT_GROUPS = ['Form 1', 'Form 2', 'Form 3', 'Form 4', 'Form 5', 'Form 6']


def populate_default_groups(apps, schema_editor):
    ClassGroup = apps.get_model('core', 'ClassGroup')
    for name in DEFAULT_GROUPS:
        ClassGroup.objects.get_or_create(name=name, defaults={'is_default': True})


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_studentattendance_method_marked_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_default', models.BooleanField(default=False, help_text='Default groups (Form 1-6) cannot be deleted via the UI')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'class_groups',
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(populate_default_groups, migrations.RunPython.noop),
    ]
