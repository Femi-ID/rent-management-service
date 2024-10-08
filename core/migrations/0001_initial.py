# Generated by Django 5.0.7 on 2024-08-20 20:48

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('reg_license', models.CharField(max_length=100)),
                ('number_of_units', models.PositiveIntegerField()),
                ('owner', models.ForeignKey(limit_choices_to={'user_type': 'LANDLORD'}, on_delete=django.db.models.deletion.CASCADE, related_name='house_details', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HouseUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_number', models.CharField(max_length=10, unique=True)),
                ('unit_type', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('rent_price', models.PositiveIntegerField(blank=True, null=True)),
                ('availability', models.BooleanField(default=False)),
                ('house', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='units', to='core.house')),
            ],
        ),
        migrations.CreateModel(
            name='LeaseAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(upload_to='files/lease_agreements/')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('house_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lease_agreements', to='core.houseunit')),
            ],
        ),
    ]
