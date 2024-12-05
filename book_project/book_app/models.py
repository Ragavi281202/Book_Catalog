from django.db import models
from django.contrib.auth.models import User

class BookCatalog(models.Model):
    book_id = models.CharField(unique=True, max_length=15, blank=True, null=True)
    cover_image_url = models.CharField(max_length=200, blank=True, null=True)
    book_title = models.CharField(max_length=300, blank=True, null=True)
    book_details = models.TextField(blank=True, null=True)
    publication_info = models.CharField(max_length=100, blank=True, null=True)
    authorlink = models.CharField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    num_pages = models.CharField(max_length=50, blank=True, null=True)
    genres = models.CharField(max_length=300, blank=True, null=True)
    num_ratings = models.IntegerField(blank=True, null=True)
    num_reviews = models.IntegerField(blank=True, null=True)
    average_rating = models.FloatField(blank=True, null=True)
    rating_distribution = models.CharField(max_length=300, blank=True, null=True)
    image_url = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'book_catalog'
        managed = True
        
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('BookCatalog', models.DO_NOTHING, to_field='book_id', blank=True, null=True)
    content = models.TextField()

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('BookCatalog', models.DO_NOTHING, to_field='book_id', blank=True, null=True)
    score = models.PositiveIntegerField()