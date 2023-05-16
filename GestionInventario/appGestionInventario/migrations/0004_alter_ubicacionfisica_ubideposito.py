# Generated by Django 4.2.1 on 2023-05-13 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionInventario', '0003_alter_ubicacionfisica_ubideposito'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ubicacionfisica',
            name='ubiDeposito',
            field=models.SmallIntegerField(choices=[(1, 'Deposito 1'), (2, 'Deposito 2'), (3, 'Deposito 3')], db_comment='Número de bodega: 1,2,3,4..'),
        ),
    ]
