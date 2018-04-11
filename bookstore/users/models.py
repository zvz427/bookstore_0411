from django.db import models
from database.basemodel import BaseModel
from utils.get_hash import get_hash
# Create your models here.
class PassportManage(models.Manager):

    def add_one_passport(self,username,password,email):
        # 插入数据的passport的值为什么，需要返回的对象是什么，有什么方法？？？？？？？？？？？？？？？？
        try:
            passport = self.create(username=username,password=get_hash(password),email=email)
        except Exception as e:
            print('错误原因',e)
            passport = None
        return passport

    def get_one_passport(self,username,password):
        try:
            passport = self.get(username=username,password=get_hash(password))
        except self.model.DoesNotExist:
            passport = None
        return passport

    def check_passport(self,username):
        try:
            passport = self.get(username=username)
        except Exception as e:
            passport = None
        if passport:
            return True
        return False



class Passport(BaseModel):
    username = models.CharField(unique=True,max_length=20,verbose_name='用户名')
    password = models.CharField(max_length=40,verbose_name='用户密码')
    email = models.EmailField(verbose_name='用户邮箱')
    is_active = models.BooleanField(default=False,verbose_name='激活状态')

    object = PassportManage()
    objects = PassportManage()#激活验证码时需要使用原生的objects，重新增加

    def __str__(self):
        return self.username

    class Meta:
        db_table = 's_user_account'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

class AddressManage(models.Manager):
    def get_default_address(self,passport_id):
        try:
            addr = self.get(passport_id=passport_id,is_default=True)
        except self.model.DoesNotExist:
            addr = None
        return addr

    def add_one_address(self,passport_id,recipient_name,recipient_addr,zip_code,recipient_phone):
        addr = self.get_default_address(passport_id=passport_id)
        if addr:
            is_default = False
        else:
            is_default = True
        addr = self.create(passport_id=passport_id,
                           recipient_name=recipient_name,
                           recipient_addr=recipient_addr,
                           zip_code=zip_code,
                           recipient_phone=recipient_phone,
                           is_default=is_default
                           )
        return addr

class Address(BaseModel):
    recipient_name = models.CharField(max_length=20,verbose_name='收件人')
    recipient_addr = models.CharField(max_length=256,verbose_name='收件地址')
    zip_code = models.CharField(max_length=6,verbose_name='邮政编码')
    recipient_phone = models.CharField(max_length=11,verbose_name='联系电话')
    is_default = models.BooleanField(default=False,verbose_name='是否默认地址')
    passport = models.ForeignKey('Passport',verbose_name='账户')

    objects = AddressManage()

    def __str__(self):
        return self.recipient_addr

    class Meta():
        db_table = 's_user_address'
        verbose_name = '收货信息'
        verbose_name_plural = verbose_name
