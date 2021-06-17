"""sample_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import sample_django.views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', sample_django.views.order),
    path('order_confirm', sample_django.views.order_confirm, name='order_confirm'),
    path('result', sample_django.views.order_result, name='order_result'),
    path('pay_confirm', sample_django.views.pay_confirm, name='pay_confirm'),
    path('pay_refund', sample_django.views.pay_refund, name='pay_refund'),
    path('auth', sample_django.views.authenticate, name='auth'),
]
