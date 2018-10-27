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
from financial.views import home, export_debts_excel, make_penalties, send_mail_to_debtors, send_email_situation, monthly_entrances

urlpatterns = [
    url('admin/', admin.site.urls),
    url('^$', home, name='home'),
    url('^debtors.xlsx$', export_debts_excel, name='export_debts_excel'),
    url('^make_penalties$', make_penalties, name='make_penalties'),
    url('^send_mail_to_debtors$', send_mail_to_debtors, name='send_mail_to_debtors'),
    url('^send_email_situation/(?P<id>\d+)$', send_email_situation, name='send_email_situation'),
    url('^monthly_entrances/(?P<month>\d+)/(?P<year>\d+)$', monthly_entrances, name='monthly_entrances'),
    

    

    
    #path('financial/', include('financial.urls')),
]
