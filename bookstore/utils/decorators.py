from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

def login_required(view_func):
    def wrapper(request,*view_args,**view_kwargs):
        if request.session.has_key('islogin'):
            return view_func(request,*view_args,**view_kwargs)
        else:
            return redirect(reverse('users:login'))
    return wrapper