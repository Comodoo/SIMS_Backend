from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0005_course_department_semester_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='class_group',
            field=models.CharField(
                blank=True,
                help_text='Class group this subject belongs to, e.g. Form 1, Form 2',
                max_length=100,
                null=True,
            ),
        ),
    ]
