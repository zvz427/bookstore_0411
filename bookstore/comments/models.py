from django.db import models
from database.basemodel import BaseModel
from users.models import Passport
from books.models import Books

# Create your models here.
class Comments(BaseModel):
    disables = models.BooleanField(default=False,verbose_name='禁止评论')
    user = models.ForeignKey('users.Passport',verbose_name='用户ID')
    book = models.ForeignKey('books.Books',verbose_name='书籍ID')
    content = models.CharField(max_length=1000,verbose_name='评论内容')

    def __str__(self):
        return self.user

    class Meta:
        db_table = 's_comments_table'