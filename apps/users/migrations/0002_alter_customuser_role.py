from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('STUDENT', 'Студент'),
                    ('INSTRUCTOR', 'Преподаватель'),
                    ('ADMIN', 'Администратор'),
                ],
                default='STUDENT',
                max_length=20,
                verbose_name='Роль',
            ),
        ),
    ]
