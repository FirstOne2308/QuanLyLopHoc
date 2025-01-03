# Generated by Django 5.1.3 on 2024-12-14 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school_app', '0006_ketqua_diem_tong'),
    ]

    operations = [
        migrations.CreateModel(
            name='KetQuaMonHoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diem_tong_ket', models.FloatField(blank=True, null=True)),
                ('hoc_sinh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_app.hocsinh')),
                ('mon_hoc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_app.monhoc')),
                ('nam_hoc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_app.namhoc')),
            ],
        ),
        migrations.CreateModel(
            name='KetQuaNamHoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diem_tong_ket', models.FloatField(blank=True, null=True)),
                ('ket_qua', models.CharField(blank=True, choices=[('Dat', 'Đạt'), ('KhongDat', 'Không đạt')], max_length=10, null=True)),
                ('hoc_sinh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_app.hocsinh')),
                ('nam_hoc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='school_app.namhoc')),
            ],
        ),
    ]
