# Generated by Django 4.2.1 on 2023-05-13 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionInventario', '0002_devolutivo_devubicacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ubicacionfisica',
            name='ubiDeposito',
            field=models.SmallIntegerField(choices=[('Deposito 1', 1), ('Deposito 2', 2), ('Deposito 3', 3), ('Deposito 4', 4)], db_comment='Número de bodega: 1,2,3,4..'),
        ),
    ]
