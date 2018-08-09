# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import *
from django.contrib import messages

admin.site.site_header = "Administracao da Comissao Financeira"
admin.site.index_title = "Administracao da Comissao Financeira"
admin.site.site_title = "Site de Administracao da Comissao Financeira"

def make_penalty(modeladmin, request, queryset):
    for debt_info in DebtInfo.objects.filter(type='1'):
        print(debt_info)
        debt_info.penalty = debt_info.penalty + 5
        debt_info.save()
make_penalty.short_description = "gerar multas para IPCs"  

def get_value(modeladmin, request, queryset):
    value = sum([entrance.value for entrance in Entrance.objects.all()])
    messages.add_message(request, messages.WARNING, 'Saldo atual: R$ %.2f!'%value)
get_value.short_description = "Obter saldo atual" 

def export_debts(modeladmin, request, queryset):
    pass

export_debts.short_description = "exportar devedores" 


class Debt_Admin(admin.ModelAdmin):
    list_display = ['student', 'paid','exemption','debt_info']
    search_fields = ['student__name',]
    list_filter=('student__name','debt_info__type', 'paid', 'exemption')
    #actions=[atualiza_pagamentos,tira_da_lista_de_espera,export_xls,exportar_usuarios_sem_inscricao]

class DebtInfo_Admin(admin.ModelAdmin):
    search_fields = ['student__name',]
    list_filter=('type',)
    actions = (make_penalty,)

class EntranceAdmin(admin.ModelAdmin):
    actions = (get_value,)


admin.site.register(Student)
admin.site.register(Entrance, EntranceAdmin)
admin.site.register(DebtInfo,  DebtInfo_Admin)
admin.site.register(Debt, Debt_Admin)
admin.site.register(Credit)