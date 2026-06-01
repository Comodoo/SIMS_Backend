from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_classgroup_is_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='classgroup',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                help_text='Parent level (e.g. Form 1 is parent of Form 1A, Form 1B)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sub_groups',
                to='core.classgroup',
            ),
        ),
    ]
