# Generated by Django 5.1.3 on 2024-12-02 09:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0012_alter_rating_book'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='book_app.bookcatalog', to_field='book_id'),
        ),
    ]
