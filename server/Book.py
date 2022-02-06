from .Db import get_db
from bs4 import BeautifulSoup as bs
import requests

url_NDL = 'https://iss.ndl.go.jp/api/opensearch?mediatype=1'


def isisbn(isbn) -> bool:
    '''
    check ISBN format
    '''
    isbn = str(isbn)
    if isbn.isdigit() is False:
        return False
    if len(isbn) != 13 and len(isbn) != 10:
        return False

    if len(isbn) == 13:
        sum = 0
        for i in range(0, 12):
            if i % 2 == 0:
                sum += int(isbn[i]) * 1
            else:
                sum += int(isbn[i]) * 3
        if int(isbn[12]) == (10 - sum % 10) % 10:
            return True
        else:
            return False

    if len(isbn) == 10:
        sum = 0
        for i in range(0, 9):
            sum += int(isbn[i]) * (10 - i)
        if int(isbn[9]) == 11 - sum % 11:
            return True
        else:
            return False


def bs_to_str(bs_obj):
    '''
    convert Nonetype to empty string
    '''
    if bs_obj is None:
        return ''
    return bs_obj.string


def fetch_from_NDL(isbn) -> dict:
    '''
    fetch bookinfo from NDL API by isbn
    return: dict
    '''

    if isisbn(isbn) is False:
        return None

    url = url_NDL + '&isbn=' + str(isbn)
    res = requests.get(url, verify=False)
    soup = bs(res.content, 'lxml').channel.find('item')
    if len(soup) == 0:
        return None

    bookinfo = {
        'isbn': bs_to_str(soup.find('dc:identifier')),
        'title': bs_to_str(soup.find('dc:title')),
        'author': bs_to_str(soup.find('dc:creator')),
        'series': bs_to_str(soup.find('dcndl:seriestitle')),
        'volume': bs_to_str(soup.find('dcndl:volume')),
        'publisher': bs_to_str(soup.find('dc:publisher')),
        'permalink': bs_to_str(soup.find('guid')),
        'edition': bs_to_str(soup.find('dcndl:edition')),
    }
    return bookinfo


def search_from_NDL(keyword, startindex=0) -> list:
    '''
    search book from NDL API by keyword
    return: list, length is 10
    '''

    url = url_NDL + '&title=' + \
        str(keyword)+'&cnt=10' + '&idx='+str(startindex*10+1)
    res = requests.get(url)
    reslist = bs(res.content, 'lxml',
                 from_encoding='utf-8').channel.find_all('item')
    books = []
    for res in reslist:
        books.append({
            'isbn': bs_to_str(res.find('dc:identifier')),
            'title': bs_to_str(res.find('dc:title')),
            'author': bs_to_str(res.find('dc:creator')),
            'series': bs_to_str(res.find('dcndl:seriestitle')),
            'volume': bs_to_str(res.find('dcndl:volume')),
            'publisher': bs_to_str(res.find('dc:publisher')),
            'permalink': bs_to_str(res.find('guid')),
            'edition': bs_to_str(res.find('dcndl:edition')),
        })
    return books


def findone(isbn) -> dict:
    '''get bookinfo from DB:book by isbn
    table: book
    search query: isbn
    return: dict
    '''
    db = get_db()

    bookinfo = db.execute(
        'SELECT * FROM book WHERE isbn = ?', (isbn,)).fetchone()
    if bookinfo is None:
        # fetch from NDL API and insert to DB
        bookinfo = fetch_from_NDL(isbn)
        if bookinfo is None:  # not found even in NDL API
            return None
        db.execute(
            'INSERT INTO book (\
                isbn, title, author, series, volume, \
                    publisher, permalink, edition) \
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (bookinfo['isbn'], bookinfo['title'], bookinfo['author'],
             bookinfo['series'], bookinfo['volume'], bookinfo['publisher'],
             bookinfo['permalink'], bookinfo['edition']))
        db.commit()

    return dict(bookinfo)
