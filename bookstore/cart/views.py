from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from django_redis import get_redis_connection
from utils.decorators import login_required
# Create your views here.

def cart_add(request):
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'请先登录！'})

    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')

    if not all([books_id,books_count]):
        return JsonResponse({'res':1,'errmsg':'数据不完整！'})

    books = Books.objects.get_book_by_id(book_id=books_id)
    if not books:
        return JsonResponse({'res':2,'errmsg':'商品不存在！'})

    try:
        count = int(books_count)
    except Exception as e:
        return JsonResponse({'res':3,'errmsg':'商品数量不合法！'})

    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')
    res = conn.hget(cart_key,books_id)

    if res is None:
        res = count
    else:
        res = int(res) + count

    if res > books.stock:
        return JsonResponse({'res':4,'errmsg':'商品库存不足！'})
    else:
        # res为每个用户每种商品的数量
        conn.hset(cart_key,books_id,res)
    return JsonResponse({'res':5,'msg':'成功添加！'})

def cart_count(request):
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0})

    conn = get_redis_connection('default')
    #前面的login_check登录界面记录了session的用户id，此处获取
    cart_key = 'cart_%d' % request.session.get('passport_id')
    res = 0
    res_list = conn.hvals(cart_key)
    print('用户储存在redis中的购物车的商品总数量',res_list)
    for i in res_list:
        res += int(i)

    return JsonResponse({'res':res})

@login_required
def cart_show(request):
    passport_id = request.session.get('passport_id')

    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id
    res_dict = conn.hgetall(cart_key)
    print('用户储存在redis中的购物车的每种商品的数量',res_dict)

    books_li = []
    total_count = 0
    total_price = 0

    for book_id,book_count in res_dict.items():
        book = Books.objects.get_book_by_id(book_id=book_id)
        book.count = book_count
        book.amount = int(book_count)*book.price
        books_li.append(book)

        total_count += int(book_count)
        total_price += int(book_count)*book.price

    context = {
        'books_li':books_li,
        'total_price':total_price,
        'total_count':total_count,
    }

    return render(request,'cart/cart.html',context)

def cart_del(request):
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'请先登录！'})

    books_id = request.POST.get('books_id')

    if not all([books_id]):
        return JsonResponse({'res':1,'errmsg':'数据不完整！'})

    book = Books.objects.get_book_by_id(book_id=books_id)
    if not book:
        return JsonResponse({'res':2,'errmsg':'商品不存在！'})

    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')
    conn.hdel(cart_key,books_id)
    return JsonResponse({'res':3})

def cart_update(request):
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'请先登录！'})

    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')

    if not all([books_id,books_count]):
        return JsonResponse({'res':1,'errmsg':'数据不完整'})

    books = Books.objects.get_book_by_id(book_id=books_id)

    if books is None:
        return JsonResponse({'res':2,'errmsg':'商品不存在!'})

    try:
        books_count = int(books_count)
    except Exception as e:
        return JsonResponse({'res':3,'errmsg':'商品数量必须为数字！'})

    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % request.session.get('passport_id')

    if books_count > books.stock:
        return JsonResponse({'res':4,'ermsg':'商品库存不足！'})

    conn.hset(cart_key,books_id,books_count)
    return JsonResponse({'res':5})












