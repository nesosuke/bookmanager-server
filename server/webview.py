from flask import Blueprint, Flask, render_template

from server import book, record, user

bp = Blueprint('web', __name__, url_prefix='/web')


class User:
    def __init__(self, username, password):
        self.isvalid = user.validate_user(username, password)

        if self.isvalid:
            self.id = user.findone(username)
            self.name = username
        else:
            self.id = None
            self.name = None


class Book:
    def __init__(self, isbn):
        self.isbn = isbn
        self.info = book.findone(isbn)

        self.id = self.info['id']
        self.title = self.info['title']
        self.author = self.info['author']
        self.publisher = self.info['publisher']
        self.series = self.info['series']
        self.volume = self.info['volume']
        self.edition = self.info['edition']
        self.perm = self.info['permalink']


class Record:
    def __init__(self, username, isbn):
        self.username = username
        self.isbn = isbn
        self.user_id = user.findone(username)
        self.book_id = book.findone(isbn)
        self.id = record.find_id(self.user_id, self.book_id)
        self.info = record.findone(self.id)

        self.status = self.info['status']
        self.rating = self.info['rating']
        self.comment = self.info['comment']
        self.record_at = self.info['record_at']


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/book/<isbn>')
def book_detail(isbn):
    book = Book(isbn).info
    return render_template('bookdetail.html', book=book)


@bp.route('/record/<record_id>') #TODO
def record_detail(record_id):

