# Generated by Django 5.1 on 2024-08-27 22:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('MAINT', 'Maintenance'), ('UTIL', 'Utility'), ('PAY', 'Payment')], max_length=100)),
                ('status', models.CharField(choices=[('RESOLVED', 'Open'), ('PROCESSING', 'In Process'), ('DECLINED', 'Declined')], max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.houseunit')),
            ],
        ),
    ]