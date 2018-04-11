from django.conf.urls import url
from users import views

urlpatterns = [
    url(r'^register/$',views.register,name='register'),
    url(r'^register_handler/$',views.register_handler,name='register_handler'),
    url(r'^login/$',views.login,name='login'),
    url(r'^login_check/$',views.login_check,name='login_check'),
    url(r'^logout/$',views.logout,name='logout'),
    url(r'^$',views.user,name='user'),
    url(r'^address/$', views.address, name='address'),
    url(r'^order/$',views.order,name='order'),
    url(r'^verifycode/$',views.verifycode,name='verifycode'),
    url(r'^active/(?P<token>.*)/$',views.register_active,name='register_active'),

]