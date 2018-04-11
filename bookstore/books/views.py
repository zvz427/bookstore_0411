from django.shortcuts import render,redirect
from books.models import Books
from utils.constant import *
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection
# Create your views here.

# 页面缓存60秒×1分钟
# @cache_page(60*1)
def index(request):
    python_new  = Books.objects.get_books_by_type(type_id=PYTHON,limit=3,sort='new')
    python_hot  = Books.objects.get_books_by_type(type_id=PYTHON,limit=4,sort='hot')
    javascript_new = Books.objects.get_books_by_type(type_id=JAVASCRIPT,limit=3,sort='new')
    javascript_hot = Books.objects.get_books_by_type(type_id=JAVASCRIPT,limit=4,sort='hot')
    algorithms_new = Books.objects.get_books_by_type(ALGORITHMS,3,'new')
    algorithms_hot = Books.objects.get_books_by_type(ALGORITHMS,4,'hot')
    machinelearning_new = Books.objects.get_books_by_type(MACHINELEARNING,3,'new')
    machinelearning_hot = Books.objects.get_books_by_type(MACHINELEARNING,4,'hot')
    operatingsystem_new = Books.objects.get_books_by_type(OPERATINGSYSTEM,3,'new')
    operatingsystem_hot = Books.objects.get_books_by_type(OPERATINGSYSTEM,4,'hot')
    database_new = Books.objects.get_books_by_type(DATABASE,3,'new')
    database_hot = Books.objects.get_books_by_type(DATABASE,4,'hot')

    context = {
        'python_hot':python_hot,
        'python_new':python_new,
        'javascript_hot':javascript_hot,
        'javascript_new':javascript_new,
        'algorithms_hot':algorithms_hot,
        'algorithms_new':algorithms_new,
        'machinelearning_hot':machinelearning_hot,
        'machinelearning_new':machinelearning_new,
        'operatingsystem_hot':operatingsystem_hot,
        'operatingsystem_new':operatingsystem_new,
        'database_new':database_new,
        'database_hot':database_hot,
    }
    return render(request,'books/index.html',context=context)

def detail(request,books_id):
    book = Books.objects.get_book_by_id(book_id=books_id)
    if not book:
        return redirect(reverse('books:index'))
    books_li = Books.objects.get_books_by_type(type_id=book.type_id,limit=2,sort='new')

    if request.session.has_key('islogin'):
        con = get_redis_connection('default')
        key = 'history_%d' % request.session.get('passport_id')
        con.lrem(key,0,books_id)
        con.lpush(key,books_id)
        con.ltrim(key,0,4)

    context = {'book':book,'books_li':books_li}
    return render(request,'books/detail.html',context=context)

def list(request,type_id,page):
    sort = request.GET.get('sort','default')
    if int(type_id) not in BOOKS_TYPE.keys():
        return redirect(reverse('books:index'))
    books_li = Books.objects.get_books_by_type(type_id=type_id,sort=sort)
    paginator = Paginator(books_li,1)
    numpages = paginator.num_pages
    if page == '' or int(page) > numpages:
        page = 1
    else:
        page = int(page)
    books_li = paginator.page(page)

    if numpages < 5:
        pages = range(1,numpages+1)
    elif numpages <= 3:
        pages = range(1,5)
    elif numpages - page <= 2:
        pages = range(numpages-4,numpages+1)
    else:
        pages = range(page+2,page+3)

    books_new = Books.objects.get_books_by_type(type_id=type_id,limit=2,sort='new')
    type_title = BOOKS_TYPE[int(type_id)]
    context = {
        'books_li' : books_li,
        'books_new': books_new,
        'type_id': type_id,
        'sort': sort,
        'type_title': type_title,
        'pages':pages,
    }
    return render(request,'books/list.html',context=context)

