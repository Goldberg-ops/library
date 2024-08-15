from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests
from bs4 import BeautifulSoup
from math import ceil
import os

db_path = os.environ.get('SQLITE_DB_PATH', 'books.sqlite')

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
"""    else:
        return 'Other'"""

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
        url = request.form['title']
        return redirect(url_for('result', title=url))
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
    params = {'q': title}
    response = requests.get('https://z-library.rs/s/', params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    book_table = soup.find("table", class_="resItemTable")
    if book_table:
        a = book_table.find("a", href=True)
        if a:
            b = a['href']
            image = book_table.find("img")
            im = image['data-srcset'].split(',')[1].split(' ')[1]

            response = requests.get(f'https://z-library.rs{b}')
            soup = BeautifulSoup(response.text, 'html.parser')
            
            ka = soup.find("a", class_="btn btn-primary dlButton addDownloadedBook reader-link")
            title_elem = soup.find("h1", itemprop="name")
            
            if ka and title_elem:
                title = title_elem.get_text().strip()
                lien = ka['href']
                category = get_category(title)
                
                cursor.execute("INSERT INTO books (title, link, image, category) VALUES (?, ?, ?, ?)", (title, lien, im, category))
                conn.commit()
                book = {'title': title, 'link': lien, 'image': im, 'category': category}
                conn.close()
                return render_template('result.html', book=book)
    
    conn.close()
    return render_template('result.html', error="Book not found")

if __name__ == '__main__':
    update_database()
    app.run(debug=False)