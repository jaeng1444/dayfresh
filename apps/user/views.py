from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic import View
from apps.user.models import User
# django发送邮件库
from django.core.mail import send_mail
from django.conf import settings
from celery import task
from django.core.urlresolvers import reverse
# Create your views here.
from itsdangerous import TimedJSONWebSignatureSerializer as S
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate,login

#
# def index(request):
#     return render(request,'register.html')


class RegisterView(View):
    '''定义一个类视图，用来判断'''
    def get(self,request):
        return render(request, 'register.html')

    def post(self,request):
        name = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        if not all([name,pwd,email]):
            return render(request,'register.html',{'meg':'输入不正确'})

        # 如果选中协议那么allow为 on
        if allow != 'on':
            return render(request, 'register.html', {'meg': '请同意协议'})

        # 判断name是否被注册，查询不在会报错，所以try
        try:
            user = User.objects.get(username = name)
        except Exception as e:
            user = None
        if user:
            return render(request, 'register.html', {'meg': '用户名已被注册'})
        user = User.objects.create_user(name, email, pwd)
        # 设置激活状态为0
        user.is_active = 0
        user.save()
        mes = '欢迎注册天天生鲜'
        print(email)
        print(name)
        # send_mail('注册激活',mes,'18519144462@163.com',[email])

        # 加密用户信息，生成激活token
        s = S(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = s.dumps(info) # bytes
        token = token.decode() # str
        print(token)
        print(type(token))
        # 发送激活邮件，邮件中包含激活链接， /user/activte/用户id
        # 发送激活链接时，先对用户身份信息进行加密，把加密后的内容放到激活链接中
        # 找其他人帮助发邮件 celery：异步完成任务
        # html_mes = '<h1>%s, 欢会员</h1>请点号<br/><a href="http://127.0.0.1:8000/user/active/%s">http:s</a>' % (name, token)
        # send_mail('注册激活',mes,'18519144462@163.com',[email],html_message=html_mes)
        # 一定一定一定一定一定一定奥调用.delay()方法
        send_register_active_email.delay(email,name,token)

        return redirect(reverse('goods:index'))


class ActiveView(View):
    def get(self,request,token):
        # 接受过来是加密的信息，所以需要解密，然后和数据库中user.id 做对比
        # 如果有则激活
        s = S(settings.SECRET_KEY,3600)
        try:
            # 解密
            info = s.loads(token)
            # 获取激活id
            user_id = info['confirm']
            # 尝试在数据库里面查询激活id是否存在
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 验证完成跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired:
            return HttpResponse('激活链接已过期')

class LoginView(View):
    def get(self, request):
        # 尝试从cookie中获取username
        if 'username' in request.COOKIES:
            # 如果有就说明记住了用户名
            username = request.COOKIES['username']
            checke = 'checked'
        else:
            # 没记住用户名
            username = ''
            checked = ''

        # 返回模板
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):
        # 如果是post方式请求，则在数据v库中查询
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        remeber = request.POST.get('remeber')

        # 参数校验。
        if all([username,pwd]):
            user = authenticate(username=username,password=pwd)
            if user is not None:
                # 判断用户是否激活
                if user.is_active:
                    # 保存用户登录状态
                    login(request,user)
                    return redirect(reverse('goods:index'))

                else:
                    return render(request, 'login.html', {'mes': '用户还未激活'})
            else:
                return render(request, 'login.html', {'mes': '用户名或密码不正确'})
        else:
            return render(request,'login.html',{'mes':'数据不完整'})
















