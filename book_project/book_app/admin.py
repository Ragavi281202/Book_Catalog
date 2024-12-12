from django.contrib import admin
from .models import BookCatalog
from django.contrib.auth.models import User

class BookProjectAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'book_title', 'author', 'average_rating')
    search_fields = ('book_id', 'book_title', 'author')
    list_filter = ('genres', 'average_rating')

admin.site.register(BookCatalog, BookProjectAdmin)