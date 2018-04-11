from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
import re
from users.models import Passport,Address
from django.http import JsonResponse,HttpResponse
from utils.decorators import login_required
from order.models import OrderInfo,OrderGoods
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from users.tasks import send_active_email
from django_redis import get_redis_connection
from books.models import Books

# Create your views here.
def register(request):
    return render(request,'users/register.html')

def register_handler(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    email = request.POST.get('email','')

    if not all([username,password,email]):
        return render(request,'users/register.html',{'errmsg':'内容不能为空'})

    # 邮箱的命名规则？？？？？？？？？？？？、
    if not re.match(r'[a-z0-9][\w\-\.]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}',email):
        return render(request,'users/register.html',{'errmsg':'邮箱命名规则错误'})

    p = Passport.object.check_passport(username=username)
    if p:
        # print('1111')
        return render(request,'users/register.html',{'errmsg':'用户名已存在！'})

    passport  = Passport.object.add_one_passport(username=username,password=password,email=email)
    #models中的Passport中的object为继承关系，只是新增加了一个object的属性，他自带的objects的其他方法还可以使用
    # Passport.object.filter()
    # Passport.objects.filter()

    # 发送注册的同步邮件确认
    serializer = Serializer(settings.SECRET_KEY, 3600)
    token = serializer.dumps(({'confirm':passport.id}))
    token = token.decode()
    # 同步发送邮件
    send_mail('尚硅谷书城用户激活（同步邮件发送）','',settings.EMAIL_FROM,[email],html_message='<a href="http://127.0.0.1:8000/users/active/%s/">http://127.0.0.1:8000/users/active/</a>' % token)

    # 发送注册的异步邮件确认
    # 加上delay才算异步celery异步发送！！！
    send_active_email.delay(token,username,email)

    return redirect(reverse('books:index'))

def login(request):
    return render(request,'users/login.html')

def login_check(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    remember = request.POST.get('remember','')
    verifycode = request.POST.get('verifycode','')

    if not all([username,password,remember,verifycode]):
        return JsonResponse({'res':2})

    if verifycode.upper() != request.session['verifycode']:
        return JsonResponse({'res': 2})

    passport = Passport.object.get_one_passport(username=username,password=password)

    if passport:
        # url_path在哪里出来的？？？？？？？？？
        # 登录的用户名没有显示？----{if else的语法写错了，没有elif}
        next_url = request.session.get('url_path',reverse('books:index'))
        jres = JsonResponse({'res':1,'next_url':next_url})

        if remember == 'true':
            jres.set_cookie('username',username,max_age=7*24*3600)
        else:
            jres.delete_cookie('username')

        request.session['islogin'] = True
        request.session['username'] = username
        request.session['passport_id'] = passport.id
        print(request.session['islogin'],'++++++++')
        # 需要返回对象
        return jres
    else:
        return JsonResponse({'res':0})

def logout(request):
    request.session.flush()
    return redirect(reverse('books:index'))

@login_required
def user(request):
    #上面的login_check登录界面记录了session的用户id，此处获取
    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)

    con = get_redis_connection('default')
    key = 'history_%d' % passport_id
    history_li = con.lrange(key,0,4)

    books_li = []
    for id in history_li:
        books = Books.objects.get_book_by_id(book_id=id)
        books_li.append(books)

    context = {
        'addr':addr,
        'page':'user',#定义何用？？？？？？？？？
        'books_li':books_li,
    }
    return render(request,'users/user_center_info.html',context)


@login_required
def address(request):
    passport_id = request.session.get('passport_id')

    if request.method == 'GET':
        addr = Address.objects.get_default_address(passport_id=passport_id)
        # page是用来干嘛的？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？
        return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})
    else:
        recipient_name = request.POST.get('username')
        recipient_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone')

        if not all([recipient_addr,recipient_name,recipient_phone,zip_code]):
            return render(request,'users/user_center_site.html',{'errmsg':'参数不能为空！'})

        Address.objects.add_one_address(
            passport_id=passport_id,
            recipient_phone=recipient_phone,
            recipient_name=recipient_name,
            recipient_addr=recipient_addr,
            zip_code=zip_code,
        )
        return redirect(reverse('users:address'))


@login_required
def order(request):
    passport_id = request.session.get('passport_id')

    order_li = OrderInfo.objects.filter(passport_id=passport_id)

    for order in order_li:
        order_id = order.order_id
        order_books_li = OrderGoods.objects.filter(order_id=order_id)

        for order_books in order_books_li:
            count = order_books.count
            price = order_books.price
            amount = count * price
            order_books.amount = amount
            print('+++++++++++++++++',count,amount)

        order.order_books_li = order_books_li

    context = {
        'order_li':order_li,
        'page':'order',
    }
    return render(request,'users/user_center_order.html',context=context)

def verifycode(request):
    from PIL import Image,ImageDraw,ImageFont
    import random
    bgcolor = (random.randrange(20,100),random.randrange(20,100),255)
    width = 100
    height = 25
    im = Image.new('RGB',(width,height),bgcolor)
    draw = ImageDraw.Draw(im)
    for i in range(100):
        xy = (random.randrange(0,width),random.randrange(0,height))
        fill = (random.randrange(0,255),255,random.randrange(0,255))
        draw.point(xy,fill=fill)
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0,len(str1))]
    font = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu-font-family/UbuntuMono-R.ttf',15)
    fontcolor = (255,random.randrange(0,255),random.randrange(0,255))
    for i in range(1,5):
        draw.text((i*20,2),rand_str[i-1],font=font,fill=fontcolor)
    del draw
    request.session['verifycode'] = rand_str
    import io
    buf = io.BytesIO()
    im.save(buf,'png')
    return HttpResponse(buf.getvalue(),'image/png')


def register_active(request,token):
    serializer = Serializer(settings.SECRET_KEY,3600)
    try:
        info = serializer.loads(token)
        passport_id = info['confirm']
        print('++++++++++++++++++++++++++++++++++',passport_id)
        passport = Passport.objects.get(id=passport_id)
        passport.is_active = True
        passport.save()
        return redirect(reverse('users:login'))
    except SignatureExpired:
        return HttpResponse('激活链接已失效！')

