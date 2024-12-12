import uvicorn,json
from fastapi import FastAPI,HTTPException
import MySQLdb
import mysql
from mysql.connector import Error
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from decouple import config
from log_module import setup_logging

app = FastAPI()

logger = setup_logging()

# def db_connect():
#     try:
#         return MySQLdb.connect(
#             host=config('DB_HOST'),
#             user=config('DB_USER'),
#             password=config('DB_PASSWORD'),
#             database=config('DB_NAME'),
#             port=int(config('DB_PORT'))
#         )
#     except MySQLdb.Error as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail="Database connection failed")

def db_connect():
    return mysql.connector.connect(
        host=config('DB_HOST'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        database=config('DB_NAME'),
        port=config('DB_PORT'),
        auth_plugin='mysql_native_password'
    )
  
def books_count():
    conn = db_connect()
    cursor = conn.cursor()
    query = "select count(book_id) from book_project"
    cursor.execute(query)
    values = cursor.fetchall()
    logger.info("books count fetched successfully")
    conn.close()
    return values[0][0]

def author_count():
    conn = db_connect()
    cursor = conn.cursor()
    query = "select count(distinct author) from book_project;"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return values[0][0]

def five_star_count():
    conn = db_connect()
    cursor = conn.cursor()
    query = "select count(*) from book_project where average_rating=(select max(average_rating) from book_project)"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return values[0][0]

def top_five_books():
    conn = db_connect()
    cursor = conn.cursor()
    query = "select cover_image_url,book_title,author from book_project  where average_rating=(select max(average_rating) from book_project) order by length(book_title) limit 5;"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return values

def top_five_authors():
    conn = db_connect()
    cursor = conn.cursor()
    query = "SELECT author, COUNT(book_id) AS Number_of_Books FROM book_project GROUP BY author ORDER BY Number_of_Books DESC LIMIT 5"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return {author : count for author,count in values}

def ratings_count():
    conn = db_connect()
    cursor = conn.cursor()
    query = "SELECT CASE WHEN average_rating <= 1 THEN '<=1' WHEN average_rating BETWEEN 1 AND 2 THEN '1 to 2' WHEN average_rating BETWEEN 2 AND 3 THEN '2 to 3' WHEN average_rating BETWEEN 3 AND 4 THEN '3 to 4' WHEN average_rating BETWEEN 4 AND 5 THEN '4 to 5' END AS rating_range, COUNT(*) AS rating_count FROM book_project GROUP BY rating_range ORDER BY rating_count DESC"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return {average_rating:count for average_rating, count in values}

# @app.get('/search_author/{author}')
# async def search_author(author: str):
#     conn = db_connect()
#     cursor = conn.cursor()
#     query="""
#             SELECT 
#             b.id,
#             b.book_title,
#             b.author,
#             b.genres,
#             b.average_rating,
#             GROUP_CONCAT(bi.images_url) AS images
#         FROM 
#             book_project b
#         LEFT JOIN 
#             book_images bi ON b.id = bi.id
#         WHERE 
#             b.author = %s
#         GROUP BY 
#             b.id
# 		order by average_rating desc;"""
#     cursor.execute(query,(author,))
#     books = cursor.fetchall()
#     columns = [col[0] for col in cursor.description]
#     books_dict = [dict(zip(columns, book)) for book in books]
#     for book in books_dict:
#         book['images'] = book['images'].split(',') if book['images'] else []
#     cursor.close()
#     conn.close()
#     return books_dict

@app.get('/search_author/{author}')
async def search_author(author: str):
    conn = db_connect()
    cursor = conn.cursor()
    query="select id,book_title,author,genres,average_rating,cover_image_url FROM book_project where author = %s group by id order by average_rating desc"
    cursor.execute(query,(author,))
    results = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    books_dict = [dict(zip(columns, book)) for book in results]
    cursor.close()
    conn.close()
    return books_dict

# @app.get('/search_generes/{genre}')
# async def search_genres(genre: str):
#     conn = db_connect()
#     cursor = conn.cursor()
#     query = f"""
#             SELECT 
#             b.id,
#             b.book_title,
#             b.author,
#             b.genres,
#             b.average_rating,
#             GROUP_CONCAT(bi.images_url) AS images
#         FROM 
#             book_project b
#         LEFT JOIN 
#             book_images bi ON b.id = bi.id
#         WHERE 
#             b.genres like '%{genre}%'
#         GROUP BY 
#             b.id
# 		order by average_rating desc;"""
#     cursor.execute(query)
#     books = cursor.fetchall()
#     columns = [col[0] for col in cursor.description]
#     books_dict = [dict(zip(columns, book)) for book in books]
#     for book in books_dict:
#         book['images'] = book['images'].split(',') if book['images'] else []
#     conn.close()
#     return books_dict

@app.get('/search_book_title/{q}')
async def search_book_title(q: str):
    conn = db_connect()
    cursor = conn.cursor()
    query="select id,book_title,author,genres,average_rating,cover_image_url FROM book_project where book_title = %s group by id order by average_rating desc"
    cursor.execute(query,(q,))
    results = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    books_dict = [dict(zip(columns, book)) for book in results]
    cursor.close()
    conn.close()
    return books_dict

@app.get('/search_generes/{genre}')
async def search_genres(genre: str):
    conn = db_connect()
    cursor = conn.cursor()
    query = f"select id,book_title,author,genres,average_rating,cover_image_url from book_project where genres like '%{genre}%' group by id order by average_rating desc"
    cursor.execute(query)
    books = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    books_dict = [dict(zip(columns, book)) for book in books]
    cursor.close()
    conn.close()
    return books_dict

# @app.get('/search_book_title/{q}')
# async def search_book_title(q: str):
#     conn = db_connect()
#     cursor = conn.cursor()
#     query = """
#         SELECT 
#             b.id,
#             b.book_title,
#             b.author,
#             b.genres,
#             b.average_rating,
#             GROUP_CONCAT(bi.images_url) AS images
#         FROM 
#             book_project b
#         LEFT JOIN 
#             book_images bi ON b.id = bi.id
#         WHERE 
#             b.book_title = %s
#         GROUP BY 
#             b.id
# 		order by average_rating desc;
#         """
#     cursor.execute(query, (q,))
#     books = cursor.fetchall()
#     columns = [col[0] for col in cursor.description]
#     books_dict = [dict(zip(columns, book)) for book in books]
#     for book in books_dict:
#         book['images'] = book['images'].split(',') if book['images'] else []
#     conn.close()
#     return books_dict

def book_title():
    conn = db_connect()
    cursor = conn.cursor()
    query = "select DISTINCT(book_title) from book_project"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return values

def author():
    conn = db_connect()
    cursor = conn.cursor()
    query = "select DISTINCT(author) from book_project"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return values

def genres():
    conn = db_connect()
    cursor = conn.cursor()
    query = "SELECT DISTINCT jt.genre FROM book_project,JSON_TABLE(genres,'$[*]' COLUMNS(genre VARCHAR(255) PATH '$')) AS jt WHERE JSON_VALID(genres)"
    cursor.execute(query)
    values = cursor.fetchall()
    conn.close()
    return values

@app.get('/books_count')
async def count_books():
    count_data = books_count()
    return count_data

@app.get('/author_count')
async def count_author():
    count_data = author_count()
    return count_data

@app.get('/five_star_count')
async def count_five():
    count_data = five_star_count()
    return count_data

@app.get('/top_five_books')
async def five_books():
    five_data = top_five_books()
    return five_data

@app.get('/top_five_authors')
async def top_five():
    count_author = top_five_authors()
    return count_author

@app.get('/ratings_count')
async def ratings():
    count_rating = ratings_count()
    return count_rating

@app.get('/book_title_list')
async def book_list():
    data = book_title()
    return data

@app.get('/author_list')
async def author_list():
    data = author()
    return data

@app.get('/genres_list')
async def genres_list():
    data = genres()
    return data