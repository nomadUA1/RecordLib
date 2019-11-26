# Generated by Django 3.0b1 on 2019-10-30 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cleanslate', '0003_auto_20191029_1903'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpungementPetitionTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='templates/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SealingPetitionTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='templates/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='expungement_petition_template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expugement_template_user_profiles', to='cleanslate.ExpungementPetitionTemplate'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sealing_petition_template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sealing_petition_template_user_profiles', to='cleanslate.SealingPetitionTemplate'),
        ),
        migrations.DeleteModel(
            name='PetitionTemplate',
        ),
    ]