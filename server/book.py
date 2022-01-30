from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from server.auth import login_required
from server.db import get_db
import requests
from bs4 import BeautifulSoup


requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

bp = Blueprint('book', __name__, url_prefix='/book')


def bs4totext(bs4object, default_value=""):
    if bs4object is None:
        return default_value
    else:
        return bs4object.text


def search_book_from_NDL(keyword):
    url = 'https://iss.ndl.go.jp/api/opensearch?title='+str(keyword)+'&cnt=10'
    res = requests.get(url, verify=False)
    reslist = BeautifulSoup(res.content, 'lxml').channel.find_all('item')
    books = []
    for res in reslist:
        books.append({
            'isbn': bs4totext(res.find('dc:identifier')),
            'title': bs4totext(res.find('dc:title')),
            'author': bs4totext(res.find('dc:creator')),
            'series': bs4totext(res.find('dcndl:seriestitle')),
            'volume': bs4totext(res.find('dcndl:volume')),
            'publisher': bs4totext(res.find('dc:publisher')),
            'permalink': bs4totext(res.find('guid')),
            'edition': bs4totext(res.find('dcndl:edition')),
        })  # list

    return books


@ bp.route('/')
def index():
    return render_template('book/index.html')


@ bp.route('/search', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        db = get_db()
        books = db.execute(
            'SELECT * FROM book WHERE title LIKE ?', ('%'+keyword+'%',)
        ).fetchall()
        if len(books) == 0:
            books = search_book_from_NDL(keyword)  # list
            # remove dupulicated data judgingin book
            for book in books:
                # add or replace book to database from NDL
                db.execute(
                    'INSERT OR REPLACE INTO book (isbn, title, author, series, volume, publisher, permalink, edition)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (book['isbn'], book['title'], book['author'], book['series'],
                     book['volume'], book['publisher'], book['permalink'], book['edition'])
                )
                db.commit()

                books = db.execute(
                    'SELECT * FROM book WHERE title LIKE ?', ('%'+keyword+'%',)
                ).fetchall()
        return render_template('book/search.html', books=books)
    return render_template('book/search.html')


if __name__ == '__main__':
    print(search_book_from_NDL('Python'))
