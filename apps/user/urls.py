from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register/', views.RegisterView.as_view(),name='register'), # 注册
    url(r'^active/(.*)',views.ActiveView.as_view(),name='active'), # 激活
    url(r'^login$',views.LoginView.as_view(),name='login'), # 登陆
]