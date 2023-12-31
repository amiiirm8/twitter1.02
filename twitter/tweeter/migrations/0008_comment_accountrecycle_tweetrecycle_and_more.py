# Generated by Django 4.2.2 on 2023-07-27 13:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tweeter', '0007_rename_homepage_link_profile_website_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='AccountRecycle',
            fields=[
            ],
            options={
                'verbose_name': 'Recycle Profile',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tweeter.profile',),
            managers=[
                ('archived', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TweetRecycle',
            fields=[
            ],
            options={
                'verbose_name': 'Recycle Tweet',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tweeter.tweet',),
            managers=[
                ('archived', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='Instagram_link',
            new_name='instagram_link',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='Website_link',
            new_name='website_link',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='date_modified',
        ),
        migrations.AddField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(default='2000-01-01', verbose_name='Birthdate'),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is_Active'),
        ),
        migrations.AddField(
            model_name='tweet',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='media',
            field=models.ImageField(blank=True, null=True, upload_to='tweet_media/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_bio',
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='body',
            field=models.CharField(max_length=280),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='tweet_likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tweets', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='media/')),
                ('tweet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_files', to='tweeter.tweet')),
            ],
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comments', models.ManyToManyField(blank=True, related_name='hashtag_comments', to='tweeter.comment')),
                ('likes', models.ManyToManyField(blank=True, related_name='hashtag_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tweeter.profile', verbose_name='Author'),
        ),
        migrations.AddField(
            model_name='comment',
            name='tweet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_set', to='tweeter.tweet'),
        ),
        migrations.AddField(
            model_name='tweet',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='tweet_comments', to='tweeter.comment'),
        ),
        migrations.AddField(
            model_name='tweet',
            name='hashtags',
            field=models.ManyToManyField(blank=True, related_name='tweets', to='tweeter.hashtag'),
        ),
    ]
