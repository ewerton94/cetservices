# -*- coding: utf-8 -*-
import os
import sys

sys.path.append('/srv/www/ctec-pet-christopher/cetservices')

os.environ['PYTHON_EGG_CACHE'] = '/srv/www/ctec-pet-christopher/cetservices/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'cetservices.settings'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

'''
def application(environ, start_response):
    status = '200 OK'
    output = 'Bem vindo ao PET Ciencia e Tecnologia!\nEstamos passando por manutencao e estaremos disponiveis em Breve'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
'''
