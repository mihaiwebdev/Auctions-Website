# Generated by Django 4.1.4 on 2022-12-13 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_comment_listing_rename_bids_bid_delete_comments_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='listings',
            field=models.ManyToManyField(blank=True, related_name='user_listings', to='auctions.listing'),
        ),
    ]
