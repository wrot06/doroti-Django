# Generated by Django 5.1.6 on 2025-02-16 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplicacion1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndiceTemp',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('id2', models.IntegerField()),
                ('Caja', models.IntegerField(blank=True, null=True)),
                ('Carpeta', models.IntegerField(blank=True, null=True)),
                ('DescripcionUnidadDocumental', models.TextField(blank=True, null=True)),
                ('NoFolioInicio', models.IntegerField(blank=True, null=True)),
                ('NoFolioFin', models.IntegerField(blank=True, null=True)),
                ('paginas', models.IntegerField()),
                ('Soporte', models.CharField(blank=True, max_length=50, null=True)),
                ('FechaIngreso', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'IndiceTemp',
                'ordering': ['id2'],
            },
        ),
    ]
