# Generated by Django 5.1 on 2024-08-31 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_houseunit_id_alter_leaseagreement_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaseagreement',
            name='rent_due_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='leaseagreement',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
