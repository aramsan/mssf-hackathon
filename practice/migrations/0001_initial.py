# Generated by Django 2.1.2 on 2018-10-08 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status_id', models.BigIntegerField(db_index=True, default=0)),
                ('screen_name', models.CharField(db_index=True, max_length=128)),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(db_index=True)),
            ],
        ),
    ]