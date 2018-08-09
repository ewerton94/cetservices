"""cetservices URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import include, url
from financial.views import home, export_debts_excel, make_penalties, send_mail_to_debtors

urlpatterns = [
    url('admin/', admin.site.urls),
    url('^$', home, name='home'),
    url('^debtors.xlsx$', export_debts_excel, name='export_debts_excel'),
    url('^make_penalties$', make_penalties, name='make_penalties'),
    url('^send_mail_to_debtors$', send_mail_to_debtors, name='send_mail_to_debtors'),
    
    #path('financial/', include('financial.urls')),
]
