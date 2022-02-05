import time
from flask import (
    Blueprint, flash,  redirect, render_template, request, session, url_for)
from werkzeug.exceptions import abort
from server.auth import login_required
from server.db import get_db

bp = Blueprint('record', __name__, url_prefix='/record')


@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    records = db.execute(
        'SELECT id,user_id,book_id,record_at FROM record'
        ' ORDER BY record_at DESC'
    ).fetchall()
    books = {}
    users = {}
    for record in records:
        books[record['book_id']] = db.execute(
            'SELECT title FROM book WHERE id = ?', (record['book_id'],)
        ).fetchone()
        users[record['user_id']] = db.execute(
            'SELECT username FROM user WHERE id = ?', (record['user_id'],)
        ).fetchone()
    return render_template('record/index.html', records=records, books=books,
                           users=users)


@ bp.route('/<isbn>', methods=('GET', 'POST'))
@ login_required
def record(isbn):
    if isbn is None:
        return render_template('record/index.html')
    elif request.method == 'POST':
        db = get_db()
        user_id = session['user_id']
        # search book_id from book table by isbn
        book_id = db.execute(
            'SELECT id FROM book WHERE isbn = ?', (isbn,)).fetchone()['id']

        # rating = request.form['rating']
        rating = 0
        if 'rating' in request.form:
            rating = request.form['rating']
        comment = ''
        if request.form['comment'] != '':
            comment = request.form['comment']
        # time format
        record_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        db = get_db()
        error = None

        # if not book_id:
        #     error = 'Book is required.'

        if error is None:
            db.execute(
                'INSERT INTO record (user_id, book_id, rating, comment, \
                record_at)'
                ' VALUES (?, ?, ?, ?, ?)',
                (user_id, book_id, rating, comment, record_at)
            )
            db.commit()
            return redirect(url_for('record.index'))

        flash(error)
    else:  # 'GET'
        db = get_db()
        book = db.execute(
            'SELECT * FROM book WHERE isbn = ?', (isbn,)
        ).fetchone()
        record = db.execute(
            'SELECT * FROM record WHERE user_id = ? AND book_id = ?', (
                session['user_id'], isbn)
        ).fetchone()
        if book is None:
            abort(404, "Book {0} doesn't exist.".format(isbn))

        return render_template('record/record.html', book=book, record=record)


@bp.route('/detail/<record_id>', methods=['GET'])
@login_required
def detail(record_id):
    db = get_db()
    record = db.execute(
        'SELECT * FROM record WHERE id = ?', (record_id,)
    ).fetchone()
    if record is None:
        abort(404, "Record {0} doesn't exist.".format(record_id))
    book = db.execute(
        'SELECT * FROM book WHERE id = ?', (record['book_id'],)
    ).fetchone()
    return render_template('record/detail.html', record=record, book=book)
