from django.shortcuts import render
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from rbac import models
from django.shortcuts import render,redirect
from rbac.service.init_permission import init_permission
# Create your views here.
class Loginform(Form):
    username = fields.CharField(
        required=True,
        error_messages={'required': '用户名不能为空'},
        widget=widgets.TextInput(attrs={'placeholder': '用户名', 'class': 'form-control'}))
    password = fields.CharField(
        required=True,
        error_messages={'required': '密码不能为空'},
        widget=widgets.TextInput(attrs={'placeholder': '密码', 'class': 'form-control'}))
def login(request):
    if request.method=="GET":
        form = Loginform
        return render(request,"login.html",{"form":form})
    else:
        form = Loginform(request.POST)
        if form.is_valid():
            username=request.POST.get("username")
            password = request.POST.get("password")
            user = models.User.objects.filter(username=username,password=password).first()
            if user:
                request.session["user_info"]={'user_id':user.id,'uid':user.userinfo.id,'name':user.userinfo.name}
                init_permission(user, request)
            return redirect('/index/')
        return redirect('/login/')

def index(request):
    return render(request,"index.html")