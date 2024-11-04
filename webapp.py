from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
from bs4 import BeautifulSoup
from math import ceil
import os

# Set up database path
data_dir = os.path.join('/home', 'site', 'wwwroot')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

db_path = os.path.join(data_dir, 'books.sqlite')

app = Flask(__name__)

BOOKS_PER_PAGE = 100 # You can adjust this number as needed

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        title TEXT PRIMARY KEY,
        link TEXT,
        image TEXT,
        category TEXT
    )
    ''')
    conn.commit()
    return conn

def get_category(title):
    title_lower = title.lower()
    if 'python' in title_lower:
        return 'Python'
    elif 'java' in title_lower:
        return 'Java'
    elif 'c++' in title_lower :
        return 'C++'
    elif 'reverse engineering' in title_lower :
        return 'Reverse Engineering'
    else:
        return 'Other'

def update_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Add the new category column if it doesn't exist
    cursor.execute("PRAGMA table_info(books)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'category' not in columns:
        cursor.execute('ALTER TABLE books ADD COLUMN category TEXT')

    # Update existing records to set a default category
    cursor.execute("UPDATE books SET category = 'Other' WHERE category IS NULL")

    # Update Python books
    cursor.execute("UPDATE books SET category = 'Python' WHERE title LIKE '%Python%'")

    # Update Java books
    cursor.execute("UPDATE books SET category = 'Java' WHERE title LIKE '%Java%'")

    cursor.execute("UPDATE books SET category = 'C++' WHERE title LIKE '%C++%'")
    cursor.execute("UPDATE books SET category = 'Reverse Engineering' WHERE title LIKE '%Reverse Engineering%'")
    cursor.execute("UPDATE books SET category = 'Reverse Engineering' WHERE title LIKE '%Reverse Engineering%'")
    cursor.execute("UPDATE books SET category = 'Reverse Engineering' WHERE title LIKE '%Reverse-Engineering%'")

    cursor.execute("UPDATE books SET category = 'Linux' WHERE title LIKE '%Linux%'")

    conn.commit()
    conn.close()

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'All')
    conn = get_db_connection()
    
    if category == 'All':
        total_books = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
        books = conn.execute('SELECT * FROM books LIMIT ? OFFSET ?', 
                             (BOOKS_PER_PAGE, (page - 1) * BOOKS_PER_PAGE)).fetchall()
    else:
        total_books = conn.execute('SELECT COUNT(*) FROM books WHERE category = ?', (category,)).fetchone()[0]
        books = conn.execute('SELECT * FROM books WHERE category = ? LIMIT ? OFFSET ?', 
                             (category, BOOKS_PER_PAGE, (page - 1) * BOOKS_PER_PAGE)).fetchall()
    
    total_pages = ceil(total_books / BOOKS_PER_PAGE)
    
    conn.close()
    return render_template('home.html', books=books, page=page, total_pages=total_pages, max=max, min=min, category=category)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        title = request.form['title']
        return redirect(url_for('result', title=title))
    return render_template('search.html')

@app.route('/result/<title>')
def result(title):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if the title is already in the database
    cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + title + '%',))
    existing_book = cursor.fetchone()

    if existing_book:
        conn.close()
        return render_template('result.html', book=existing_book)
    
    # If not in database, search online
    url = "https://fr.1lib.sk"
    params = {'q': title}
    response = requests.get(f'{url}/s/', params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    bookcard = soup.find("z-bookcard", href=True)
    if bookcard:
            get_url = bookcard['href']
            details = bookcard.find_all("div")
            book_title = details[0].text.strip()
            response = requests.get(f'{url}{get_url}')
            soup = BeautifulSoup(response.text, 'html.parser')
            img = soup.find("div", class_="col-sm-3 details-book-cover-container").find("img")['data-src']
            book_url = soup.find("a", class_="btn btn-primary dlButton reader-link")['href']
            category = get_category(title)
            cursor.execute("INSERT INTO books (title, link, image, category) VALUES (?, ?, ?, ?)", (book_title, book_url, img, category))
            conn.commit()
            book = {'title': book_title, 'link': book_url, 'image': img, 'category': category}
            conn.close()
            return render_template('result.html', book=book)
    
    conn.close()
    return render_template('result.html', error="Book not found")
