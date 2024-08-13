from django.urls import path
from . import views



urlpatterns = [
    path('', views.count_books, name='count_books'),
    path('suggestions_search/', views.suggestions_search, name='suggestions_search'),
    path('searching/', views.searching, name='searching'),
    path('genere_search/',views.genere_search,name='genere_search')
]

