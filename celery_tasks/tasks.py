# 使用celery

from django.conf import settings
from django.core.mail import send_mail
from celery import Celery

# 创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/1')

# 定义任务函数
@app.task
def send_register_active_email(to_email,name,token):
    # 组织邮件信息
    subject = '天天生鲜欢迎信息'
    mes = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_mes = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击以下链接激活您的账号<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'%(name, token, token)
    send_mail(subject,mes,sender,receiver,html_message=html_mes)



