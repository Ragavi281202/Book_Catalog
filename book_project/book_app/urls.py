from django.urls import path
from . import views

urlpatterns = [
    path('', views.count_books, name='count_books'),
    path('count_books_updated/', views.count_books_updated, name='count_books_updated'),
    path('suggestions_search/', views.suggestions_search, name='suggestions_search'),
    path('searching/', views.searching, name='searching'),
    path('genere_search/',views.genere_search,name='genere_search'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('add-review/<int:book_id>/', views.add_review, name='add_review_search'),
    path('add-rating/<int:book_id>/', views.add_rating, name='add_rating_search'),
]

