# Generated by Django 4.2.2 on 2023-07-28 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweeter', '0008_comment_accountrecycle_tweetrecycle_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='tweets',
            field=models.ManyToManyField(related_name='posted_by', to='tweeter.tweet'),
        ),
    ]