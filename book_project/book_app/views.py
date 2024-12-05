from django.shortcuts import render,get_object_or_404, redirect
import requests
from django.http import HttpResponse, JsonResponse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from log_module import setup_logging
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout 
from .forms import RegisterForm,LoginForm
from django.contrib.auth.decorators import login_required
from .models import BookCatalog,Review,Rating
import asyncio
from django.db.models import Avg
import websockets

logger = setup_logging()

# main_url = "http://fastapi:8001"
main_url = "http://127.0.0.1:8001"

def count_books(request):
    url1 = f"{main_url}/books_count"
    url2 = f"{main_url}/author_count"
    url3 = f"{main_url}/five_star_count"
    url4 = f"{main_url}/top_five_books"
    url5 = f"{main_url}/top_five_authors"
    url6 = f"{main_url}/ratings_count"
    

    try:
        logger.info("Starting API request")
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        response3 = requests.get(url3)
        response4 = requests.get(url4)
        response5 = requests.get(url5)
        response6 = requests.get(url6)
        logger.info("API request successful")

        if response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200 and response4.status_code == 200 and response5.status_code == 200 and response6.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            data3 = response3.json()
            data4 = response4.json()
            data5 = response5.json()
            data6 = response6.json()

            top_books = [{'image': book[0], 'name': book[1], 'author': book[2]} for book in data4]
            authors = list(data5.keys())
            books_count = list(data5.values())

            fig, ax = plt.subplots(figsize=(9, 7))
            ax.pie(books_count, labels=authors, colors=['#FF9EAA', '#FFD1DC', '#FFAFC9', '#FF80A0', '#FF4D7A'], autopct='%1.1f%%')
            ax.axis('equal')
            ax.set_title('Top 5 authors with highest number of books written', fontsize=15)
            img1 = io.BytesIO()
            plt.savefig(img1, format='png')
            img1.seek(0)
            chart1_url = base64.b64encode(img1.getvalue()).decode()
            plt.close()

            ratings = list(data6.keys())
            ratings_count = list(data6.values())
            fig, ax = plt.subplots(figsize=(9, 7))
            ax.bar(ratings, ratings_count, color=['#7469B6', '#AD88C6', '#E1AFD1', '#DBC4F0', '#053657'])
            for i, v in enumerate(ratings_count):
                ax.text(i, v + 3, str(v), color='black', ha='center')
            ax.set_xlabel('Ratings Distribution')
            ax.set_ylabel('Ratings Count')
            ax.set_title('Ratings Distribution count', fontsize=15)
            img2 = io.BytesIO()
            plt.savefig(img2, format='png')
            img2.seek(0)
            chart2_url = base64.b64encode(img2.getvalue()).decode()
            plt.close()

            content = {
                'count': data1,
                'count_author': data2,
                'five_count': data3,
                'five_images': top_books,
                'chart1': chart1_url,
                'chart2': chart2_url
            }
            return render(request, "dashboard.html", content)
        
        else:
            logger.error("Failed to retrieve some API data")
            return HttpResponse("Failed to retrieve data", status=500)
    except Exception as e:
        # logger.exception(f"Error during API request: {str(e)}")
        logger.error(f"An error occurred while fetching categories: {str(e)}", exc_info=True)
        # logger.error("Traceback: %s", traceback.format_exc())
        return HttpResponse("An error occurred", status=500)

def suggestions_search(request):
    booktitle_url = f"{main_url}/book_title_list"
    author_url = f"{main_url}/author_list"
    genres_url = f"{main_url}/genres_list"
    try:
        logger.info("Starting API request")
        booktitle_response = requests.get(booktitle_url)
        author_response = requests.get(author_url)
        genres_response = requests.get(genres_url)
        logger.info("API request successful")
        
        book_title = booktitle_response.json()
        author_names = author_response.json()
        genres_data = genres_response.json()

        books_title = [book[0] for book in book_title]
        authors_title = [author[0] for author in author_names]
        genres_title = [genre[0] for genre in genres_data]

        categories = {
            "Books": books_title,
            "Authors": authors_title,
            "Genres": genres_title
        }

        suggestions = []
        if request.method == 'POST':
            category = request.POST.get('category')
            query = request.POST.get('query', '').lower()
            if category in categories:
                suggestions = [item for item in categories[category] if query in item.lower()]

        return JsonResponse({"suggestions": suggestions})
    except Exception as e:
        # logger.exception(f"Error retrieving suggestions: {str(e)}")
        logger.error(f"An error occurred while fetching categories: {str(e)}", exc_info=True)
        # logger.error("Traceback: %s", traceback.format_exc())
        return JsonResponse({"suggestions": []})

def searching(request):
    logger.info("Starting API request")
    if request.method == 'POST':
        option = request.POST.get('category')
        value = request.POST.get('query')
    else:
        option = request.GET.get('category')
        value = request.GET.get('query')

    logger.info(f"Search option: {option}, Search value: {value}")

    try:
        if option == "Books":
            response = requests.get(f"{main_url}/search_book_title/{value}")
        elif option == "Authors":
            response = requests.get(f"{main_url}/search_author/{value}")
        elif option == "Genres":
            response = requests.get(f"{main_url}/search_generes/{value}")
        else:
            raise ValueError("Invalid search option")

        data = response.json()
        if not data:
            logger.warning("Invalid data")
            return render(request, 'search.html', {'book_name': 'Invalid', 'option': option, 'query': value})

        for book in data:
            if isinstance(book.get('genres'), str):
                book['genres'] = json.loads(book['genres'])
        # for book in data:
        #     if isinstance(book.get('cover_image_url'), str):
        #         book['images'] = json.loads(book['images'])

        page = request.GET.get('page', 1)
        paginator = Paginator(data, 10)

        if int(page) > paginator.num_pages:
            page_not_found = True
            logger.warning("Page Not Found")
        try:
            books = paginator.page(page)
            page_not_found = False
        except PageNotAnInteger:
            books = paginator.page(1)
            page_not_found = False
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        
        url8= f"{main_url}/retrieve_review"
        response2=requests.get(url8)
        if response2.status_code==200:
            user_review_data= response2.json()

        context_data = {
            'book_name': books,
            'review_of_user':user_review_data,
            'option': option,
            'query': value,
            'page_not_found': page_not_found
        }
        # logger.info(f"Context Data: {context_data}")

        return render(request, 'search.html', context_data)
    except Exception as e:
        # logger.exception(f"Error during search: {str(e)}")
        logger.error(f"An error occurred while fetching categories: {str(e)}", exc_info=True)
        # logger.error("Traceback: %s", traceback.format_exc())
        return render(request, 'search.html', {'book_name': [], 'option': option, 'query': value})

def genere_search(request):
    logger.info("Starting API request")
    genre_data = request.GET.get('genre')
    try:
        if genre_data:
            response = requests.get(f"{main_url}/search_generes/{genre_data}")
            data = response.json()
        else:
            data = "Error"

        if data == "Invalid" or data == "Error":
            logger.warning("Invalid Data")
            context_data = {
                'book_name': data,
                'genre_data': genre_data
            }
            return render(request, 'search_genre.html', context_data)

        for book in data:
            if isinstance(book.get('genres'), str):
                book['genres'] = json.loads(book['genres'])
        # for book in data:
        #     if isinstance(book.get('images'), str):
        #         book['images'] = json.loads(book['images'])

        page = request.GET.get('page', 1)
        paginator = Paginator(data, 10)

        if int(page) > paginator.num_pages:
            page_not_found = True
            logger.warning("Page Not Found")
        try:
            books = paginator.page(page)
            page_not_found = False
        except PageNotAnInteger:
            books = paginator.page(1)
            page_not_found = False
        except EmptyPage:
            books = paginator.page(paginator.num_pages)

        context_data = {
            'book_name': books,
            'page_not_found': page_not_found,
            'genre_data': genre_data
        }
        logger.info(f"Context Data: {context_data}")
        return render(request, 'search_genre.html', context_data)
    except Exception as e:
        # logger.exception(f"Error during genre search: {str(e)}")

        logger.error(f"An error occurred while fetching categories: {str(e)}", exc_info=True)
        # logger.error("Traceback: %s", traceback.format_exc())
        return render(request, 'search_genre.html', {'book_name': [], 'genre_data': genre_data})
    
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            logger.info('Registration form is valid.')
            user = form.save()
            auth_login(request, user)
            logger.info(f'New user registered and logged in: {user.username}')
            return redirect('count_books')
        else:
            logger.warning('Registration form is invalid.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            logger.info('Login form is valid.')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                logger.info(f'User logged in: {username}')
                return redirect('count_books') 
            else:
                logger.warning('Authentication failed. Invalid username or password.')
        else:
            logger.warning('Login form is invalid.') 
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    user = request.user
    if user.is_authenticated:
        logger.info(f'User logged out: {user.username}')
    else:
        logger.warning('Logout attempt by unauthenticated user.')
    logout(request)
    return redirect('count_books')

async def broadcast_message(message: dict):
    websocket_url = "ws://localhost:8001/ws/notifications"
    logger.info(f'Attempting to send message to WebSocket server at {websocket_url}')
    try:
        async with websockets.connect(websocket_url) as websocket:
            logger.info(f'Connected to WebSocket server: {websocket_url}')
            await websocket.send(json.dumps(message))
            logger.info(f'Message sent: {message}')
    except Exception as e:
        logger.error(f'Error occurred while sending message to WebSocket server: {e}')

@login_required
def add_review(request, book_id):
    book = get_object_or_404(BookCatalog, id=book_id)
    if request.method == 'POST':
        review_content = request.POST.get('content')
        if review_content:
            review = Review.objects.filter(book=book, user=request.user).first()
            if review:
                review.content=review_content
                review.save()
                logger.info(f'Review updated for book_id: {book_id} by user: {request.user.username}')
            else:
                review = Review.objects.create(book=book, user=request.user, content=review_content)
                logger.info(f'Review added for book_id: {book_id} by user: {request.user.username}')

            message = {
                "type": "review",
                "username": request.user.username,
                "content": review_content
            }
            asyncio.run(broadcast_message(message))
            logger.info(f'Message broadcasted: {message}')
            return JsonResponse({'message': 'Review added/updated successfully.'})
        else:
            logger.warning('No content provided for review.')
            return JsonResponse({'error': 'No content provided for review.'}, status=400)
    logger.error('Invalid request method for add_review.')
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def add_rating(request, book_id):
    book = get_object_or_404(BookCatalog, id=book_id)
    if request.method == 'POST':
        try:
            rating_score = int(request.POST.get('content'))
            if 1 <= rating_score <= 5:
                rating = Rating.objects.filter(book=book, user=request.user).first()
                if rating:
                    rating.score=rating_score
                    rating.save()
                    logger.info(f'Rating updated for book_id: {book_id} by user: {request.user.username}')
                else:
                    rating=Rating.objects.create(book=book,user=request.user,score=rating_score)
                    logger.info(f'Rating added for book_id: {book_id} by user: {request.user.username}')
                
                avg_rating = Rating.objects.filter(book=book).aggregate(Avg('score'))['score__avg']

                message = {
                    "type": "average_rating",
                    "average_rating": avg_rating,
                    "book_id":book.book_id
                }
                asyncio.run(broadcast_message(message))
                logger.info(f'Message broadcasted: {message}')
                return JsonResponse({"message": "Rating added/updated successfully."})
            else:
                logger.warning('Rating must be between 1 and 5.')
                return JsonResponse({"error": "Rating must be between 1 and 5."}, status=400)
        except ValueError:
            logger.error('Invalid rating value provided.')
            return JsonResponse({"error": "Invalid rating value."}, status=400)
        
    logger.error('Invalid request method for add_rating.')    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def count_books_updated(request):
    url1 = f"{main_url}/books_count"
    url2 = f"{main_url}/author_count"
    url3 = f"{main_url}/five_star_count"
    url4 = f"{main_url}/top_five_books"
    url5 = f"{main_url}/top_five_authors"
    url6 = f"{main_url}/ratings_count"
    

    try:
        logger.info("Starting API request")
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        response3 = requests.get(url3)
        response4 = requests.get(url4)
        response5 = requests.get(url5)
        response6 = requests.get(url6)
        logger.info("API request successful")

        if response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200 and response4.status_code == 200 and response5.status_code == 200 and response6.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()
            data3 = response3.json()
            data4 = response4.json()
            data5 = response5.json()
            data6 = response6.json()

            top_books = [{'image': book[0], 'name': book[1], 'author': book[2]} for book in data4]
            authors = list(data5.keys())
            books_count = list(data5.values())

            fig, ax = plt.subplots(figsize=(9, 7))
            ax.pie(books_count, labels=authors, colors=['#FF9EAA', '#FFD1DC', '#FFAFC9', '#FF80A0', '#FF4D7A'], autopct='%1.1f%%')
            ax.axis('equal')
            ax.set_title('Top 5 authors with highest number of books written', fontsize=15)
            img1 = io.BytesIO()
            plt.savefig(img1, format='png')
            img1.seek(0)
            chart1_url = base64.b64encode(img1.getvalue()).decode()
            plt.close()

            ratings = list(data6.keys())
            ratings_count = list(data6.values())
            fig, ax = plt.subplots(figsize=(9, 7))
            ax.bar(ratings, ratings_count, color=['#7469B6', '#AD88C6', '#E1AFD1', '#DBC4F0', '#053657'])
            for i, v in enumerate(ratings_count):
                ax.text(i, v + 3, str(v), color='black', ha='center')
            ax.set_xlabel('Ratings Distribution')
            ax.set_ylabel('Ratings Count')
            ax.set_title('Ratings Distribution count', fontsize=15)
            img2 = io.BytesIO()
            plt.savefig(img2, format='png')
            img2.seek(0)
            chart2_url = base64.b64encode(img2.getvalue()).decode()
            plt.close()

            content = {
                'count': data1,
                'count_author': data2,
                'five_count': data3,
                'five_images': top_books,
                'chart1': chart1_url,
                'chart2': chart2_url
            }
            return JsonResponse(content)
        
        else:
            logger.error("Failed to retrieve some API data")
            return HttpResponse("Failed to retrieve data", status=500)
    except Exception as e:
        # logger.exception(f"Error during API request: {str(e)}")
        logger.error(f"An error occurred while fetching categories: {str(e)}", exc_info=True)
        # logger.error("Traceback: %s", traceback.format_exc())
        return HttpResponse("An error occurred", status=500)