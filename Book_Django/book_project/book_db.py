# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BookRagaviPriya(models.Model):
    book_id = models.CharField(unique=True, max_length=15, blank=True, null=True)
    cover_image_url = models.CharField(max_length=200, blank=True, null=True)
    book_title = models.CharField(max_length=300, blank=True, null=True)
    book_details = models.TextField(blank=True, null=True)
    format = models.CharField(max_length=100, blank=True, null=True)
    publication_info = models.CharField(max_length=100, blank=True, null=True)
    authorlink = models.CharField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    num_pages = models.CharField(max_length=50, blank=True, null=True)
    genres = models.CharField(max_length=300, blank=True, null=True)
    num_ratings = models.IntegerField(blank=True, null=True)
    num_reviews = models.IntegerField(blank=True, null=True)
    average_rating = models.FloatField(blank=True, null=True)
    rating_distribution = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book_ragavi_priya'
