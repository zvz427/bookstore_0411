from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from utils.decorators import login_required
from django.http import HttpResponse,JsonResponse
from users.models import Address
from books.models import Books
from order.models import OrderInfo,OrderGoods
from django_redis import get_redis_connection
from datetime import datetime
from django.conf import settings
import os
import time
from django.db import transaction
from alipay import AliPay

# Create your views here.

@login_required
def order_place(request):
    # return render(request,'order/place_order.html')
    #getlist是什么用法？

    # 无法得到books_ids? 前端post请求过来的数据
    books_ids = request.POST.getlist('books_ids')

    print('+++++++++++++++',books_ids)
    if not all([books_ids]):
        return redirect(reverse('cart:show'))

    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)

    books_li = []
    total_count = 0
    total_price = 0

    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % passport_id

    for id in books_ids:
        books = Books.objects.get_book_by_id(book_id=id)
        count = conn.hget(cart_key,id)
        books.count = count
        amount = int(count)*books.price
        books.amount = amount
        books_li.append(books)

        total_count += int(count)
        total_price += amount

    transit_price = 10
    total_pay = total_price + transit_price

    books_ids = ','.join(books_ids)
    context = {
        'addr':addr,
        'books_li':books_li,
        'total_count':total_count,
        'total_price':total_price,
        'total_pay':total_pay,
        'transit_price':transit_price,
        'books_ids':books_ids,
    }
    return render(request,'order/place_order.html',context)

@transaction.atomic
def order_commit(request):
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'用户未登录！'})

    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    books_ids = request.POST.get('books_ids')

    if not all([addr_id,pay_method,books_ids]):
        return JsonResponse({'res':1,'errmsg':'数据不完整！'})

    try:
        addr = Address.objects.get(id=addr_id)
    except Exception as e:
        return JsonResponse({'res':2,'errmsg':'地址信息出错！'})

    if int(pay_method) not in OrderInfo.PAY_METHOD_ENUM.values():
        return JsonResponse({'res':3,'errmsg':'不支持的支付方式！'})

    passport_id = request.session.get('passport_id')
    order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(passport_id)
    transit_price = 10

    total_count = 0
    total_price = 0

    sid = transaction.savepoint()
    try:
        order = OrderInfo.objects.create(
            order_id=order_id,
            passport_id=passport_id,
            addr_id=addr_id,
            total_count=total_count,
            total_price=total_price,
            transit_price=transit_price,
            pay_method=pay_method
        )
        books_ids=books_ids.split(',')
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % passport_id
        for id in books_ids:
            books = Books.objects.get_book_by_id(book_id=id)
            if books is None:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':4,'errmsg':'商品信息错误！'})

            count = conn.hget(cart_key,id)
            if int(count) > books.stock:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':5,'errmsg':'商品库存不足！'})

            OrderGoods.objects.create(
                order_id=order_id,
                books_id=id,
                count=count,
                price=books.price
            )

            books.sales += int(count)
            books.stock += int(count)
            books.save()

            total_count += int(count)
            total_price += int(count)*books.price
        order.total_count = total_count
        order.total_price = total_price
        order.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res':6,'errmsg':'服务器错误！'})

    conn.hdel(cart_key,*books_ids)

    transaction.savepoint_commit(sid)
    return JsonResponse({'res':7})

#支付宝的支付接口错误
def order_pay(request):
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'用户未登录！'})

    order_id = request.POST.get('order_id')

    # 去付款的页面显示错误，订单不存在？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？、
    if not order_id:
        return JsonResponse({'res':1,'errmsg':'订单不存在！'})

    try:
        order = OrderInfo.objects.get(order_id=order_id,status=1,pay_method=3)
    except OrderInfo.DoesNotExist:
        return JsonResponse({'res':2,'errmsg':'订单信息错误！'})

    alipay = AliPay(
        appid="2016090800464054", # 应用id
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(settings.BASE_DIR, 'order/app_private_key.pem'),
        alipay_public_key_path=os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem'),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type = "RSA2",  # RSA 或者 RSA2
        debug = True,  # 默认False
    )

    # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    total_pay = order.total_price + order.transit_price # decimal
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id, # 订单id
        total_amount=str(total_pay),
        subject='尚硅谷书城%s' % order_id,
        return_url=None,
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    # 返回应答
    pay_url = settings.ALIPAY_URL + '?' + order_string
    return JsonResponse({'res': 3, 'pay_url': pay_url, 'message': 'OK'})

#支付宝接口失效
def check_pay(request):
    '''获取用户支付的结果'''
    # 用户登录判断
    if not request.session.has_key('islogin'):
        return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

    passport_id = request.session.get('passport_id')
    # 接收订单id
    order_id = request.POST.get('order_id')

    # 数据校验
    if not order_id:
        return JsonResponse({'res': 1, 'errmsg': '订单不存在'})

    try:
        order = OrderInfo.objects.get(order_id=order_id,
                                      passport_id=passport_id,
                                      pay_method=3)
    except OrderInfo.DoesNotExist:
        return JsonResponse({'res': 2, 'errmsg': '订单信息出错'})

    # 和支付宝进行交互
    alipay = AliPay(
        appid="2016090800464054",  # 应用id
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(settings.BASE_DIR, 'df_order/app_private_key.pem'),
        alipay_public_key_path=os.path.join(settings.BASE_DIR, 'df_order/alipay_public_key.pem'),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True,  # 默认False
    )

    while True:
        # 进行支付结果查询
        result = alipay.api_alipay_trade_query(order_id)
        code = result.get('code')
        if code == '10000' and result.get('trade_status') == 'TRADE_SUCCESS':
            # 用户支付成功
            # 改变订单支付状态
            order.status = 2 # 待发货
            # 填写支付宝交易号
            order.trade_id = result.get('trade_no')
            order.save()
            # 返回数据
            return JsonResponse({'res':3, 'message':'支付成功'})
        elif code == '40004' or (code == '10000' and result.get('trade_status') == 'WAIT_BUYER_PAY'):
            # 支付订单还未生成，继续查询
            # 用户还未完成支付，继续查询
            time.sleep(5)
            continue
        else:
            # 支付出错
            return JsonResponse({'res':4, 'errmsg':'支付出错'})