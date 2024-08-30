# Generated by Django 5.0.7 on 2024-08-24 01:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('email', models.EmailField()),
                ('reference', models.CharField(max_length=100)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('abandoned', 'Abandoned'), ('failed', 'Failed'), ('ongoing', 'Ongoing'), ('pending', 'Pending'), ('processing', 'Processing'), ('queued', 'Queued'), ('reversed', 'Reversed'), ('success', 'Success')], default='pending', max_length=20)),
                ('transaction_id', models.BigIntegerField(blank=True, null=True)),
                ('customer_code', models.CharField(max_length=20)),
                ('authorization_code', models.CharField(max_length=20)),
                ('house_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='core.houseunit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
