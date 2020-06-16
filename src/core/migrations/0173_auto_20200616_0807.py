# Generated by Django 3.0.6 on 2020-06-16 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0172_merge_20200616_0245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='user',
        ),
        migrations.AddField(
            model_name='chat',
            name='people',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='chat', to='core.People'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='chat',
            name='channel',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_channel', to='core.Record'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='message',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
