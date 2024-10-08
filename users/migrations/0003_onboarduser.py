# Generated by Django 5.0.7 on 2024-09-20 12:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_houseunit_occupant'),
        ('users', '0002_alter_user_date_of_birth_alter_user_user_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnboardUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=250, unique=True)),
                ('house_unit', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='onboard_tenant', to='core.houseunit')),
            ],
            options={
                'ordering': ['house_unit'],
            },
        ),
    ]
