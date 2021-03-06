# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from io import BytesIO as IO
from .models import Debt, Entrance, DebtInfo, Student, EmailThread, Email
from .forms import EntranceForm, CreditForm
from django.core.mail import send_mail
from django.conf import settings
import sys
from django.contrib import messages
from datetime import datetime
from dateutil.relativedelta import relativedelta

if sys.version_info[0] < 3:
    reload(sys)  
    sys.setdefaultencoding('utf8')



def get_debtors():
    students = []
    ds = {'descricao': [], 'valor': [], 'email': [], 'id': []}
    for debt in Debt.objects.filter(paid=False, exemption=False).order_by('student'):
        students.append(debt.student.name)
        ds['id'].append(debt.student.id)
        ds['email'].append(debt.student.email)
        ds['descricao'].append(str(debt.debt_info))
        ds['valor'].append(debt.debt_info.value + debt.debt_info.penalty-debt.discount)

    return pd.DataFrame(ds, index=students)
def get_debt_description():
    df = get_debtors()
    total = df.groupby(df.index).valor.sum()
    students = []
    for row in total.index:
        value = total[row]
        data = df[df.index==row]
        if isinstance(data, pd.DataFrame):
            email = data['email'].values[0]
        descricao = data['descricao'].values
        valor = data['valor'].values
        if sys.version_info[0] < 3: # Python 3
            descricao = [d.encode('utf8') for d in descricao]
        ds = '\n'.join([str(d[0]) + ' - R$ ' +  str(d[1]) for d in list(zip(descricao, valor))])
        students.append({'id': data['id'].values[0],'nome': row, 'email': email, 'total': value, 'description': ds})
    return students

def home(request):
    if request.method == 'POST':
        credit_form = CreditForm(request.POST, prefix='credit')
        entrance_form = EntranceForm(request.POST, prefix='entrance')
        if credit_form.is_valid():
            credit_form.save()
            messages.add_message(request, messages.SUCCESS, "Pagamento cadastrado!")
        elif entrance_form.is_valid():
            entrance_form.save()
            messages.add_message(request, messages.SUCCESS, "Fluxo de caixa alterado com sucesso!")
        else:
            messages.add_message(request, messages.ERROR, "Algo ocorreu errado!")
            
    entrances = Entrance.objects.all()
    cash = round(sum([e.value for e in entrances]), 2)
    entrances = entrances.order_by('-id')[:5]
    credit_form = CreditForm(prefix='credit')
    credit_form.title = 'Cadastrar pagamento de dívida'
    entrance_form = EntranceForm(prefix='entrance')
    entrance_form.title = 'Cadastrar entrada ou saída de dinheiro'
    forms = [credit_form, entrance_form]
    students = []
    descriptions = get_debt_description()
    #print(descriptions)
    for desc in descriptions:
        student = Student.objects.get(name=desc['nome'])
        student.total = desc['total']
        students.append(student)
    now = datetime.now()
    date = '%i/%i'%(now.month, now.year)
    return render(request, 'home.html', {'entrances': entrances, 'cash': cash, 'forms': forms, 'students': students, 'BASE_URL_SITE': settings.BASE_URL_SITE, 'date': date})

def monthly_entrances(request, month, year):
    entrances = Entrance.objects.filter(
        created__year__gte=year,
        created__month__gte=month,
        created__year__lte=year,
        created__month__lte=month
    )
    cash = round(sum([e.value for e in entrances]), 2)
    entrances = entrances.order_by('-id')
    now = datetime.now()
    corrent = datetime(year=int(year), month=int(month), day=1)
    if now.month==int(month) and now.year>=int(year):
        date_after_month = None
    else:
        date_after_month = corrent + relativedelta(months=1)
        date_after_month = '%i/%i'%(date_after_month.month, date_after_month.year)
    date_before_month = corrent - relativedelta(months=1)
    date_before_month = '%i/%i'%(date_before_month.month, date_before_month.year)
    return render(request, 'entrances.html', {'entrances': entrances, 'cash': cash, 'BASE_URL_SITE': settings.BASE_URL_SITE, 'month': month, 'year': year, 'date_after_month': date_after_month, 'date_before_month': date_before_month })


def make_penalties(request):
    for debt_info in DebtInfo.objects.filter(type='1'):
        debt_info.penalty = debt_info.penalty + 5
        debt_info.save()
    messages.add_message(request, messages.SUCCESS, "Multas adicionadas!")
    return HttpResponseRedirect(settings.BASE_URL_SITE + '/')


def send_email_situation(request, id):
    for student in get_debt_description():
        if int(student['id'])==int(id):
            email_ = Email.objects.all()[0]
            msg = 'Olá %s,\n\n%s \n\nSegue abaixo a sua dívida com o PET CT: \n\n%s\n\nValor total a pagar: %.2f'%(student['nome'], email_.message, student['description'], student['total'])
            EmailThread(
                email_.subject,
                msg,
                settings.DEFAULT_FROM_EMAIL,
                [student['email']],
            ).start()
            messages.add_message(request, messages.SUCCESS, "Email de cobrança enviado para %s com sucesso."%student['email'])
    return HttpResponseRedirect(settings.BASE_URL_SITE + '/')


def send_mail_to_debtors(request):
    for student in get_debt_description():
        email_ = Email.objects.all()[0]
        msg = 'Olá %s,\n\n%s  \n\nSegue abaixo a sua dívida com o PET CT: \n\n%s\n\nValor total a pagar: %.2f'%(student['nome'], email_.message, student['description'], student['total'])
        EmailThread(
            email_.subject,
            msg,
            settings.DEFAULT_FROM_EMAIL,
            [student['email']],
        ).start()
    messages.add_message(request, messages.SUCCESS, "Email de cobrança enviado para todos os petianos devedores.")
    return HttpResponseRedirect(settings.BASE_URL_SITE + '/')



def export_debts_excel(request):
    sio = IO()
    ds = {'descricao': [], 'valor': []}
    students = []
    for debt in Debt.objects.filter(paid=False, exemption=False).order_by('student'):
        students.append(debt.student.name)
        ds['descricao'].append(str(debt.debt_info))
        ds['valor'].append(debt.debt_info.value + debt.debt_info.penalty-debt.discount)
    PandasDataFrame = pd.DataFrame(ds, index=students)
    PandasWriter = pd.ExcelWriter(sio, engine='xlsxwriter')
    PandasDataFrame.to_excel(PandasWriter, sheet_name='Debtors')
    PandasWriter.save()
    PandasWriter.close()
    sio.seek(0)
    workbook = sio.getvalue()
    response = HttpResponse(sio.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=%s' % 'devedores.xlsx'
    #messages.add_message(request, messages.SUCCESS, "Planilha de dívidas gerada com sucesso.")
    return response

'''
import json
import datetime
from .utils import *

def create_specific_debt_view():
    number = get_option_number(list_students, 'petiano')
    description = input("Insira a descrição da dívida\n>>> ")
    value = get_int_value("Qual o valor da dívida?")
    student = get_student(number)
    create_specific_debt(student, description, value)


def create_geral_debt_view():
    debt_type = get_option_number(list_debt_types, 'tipo de débito')
    month = get_int_value("Qual o mês de referência?")
    year = get_int_value("Qual o ano de referência?")
    value = get_int_value("Qual o valor da cobrança?")
    penalty = get_int_value("No caso de multas, qual o valor cobrado mensalmente?")
    create_debt(month, year, debt_type, value, penalty)
BOOLEAN = {1: True, 0: False}
def create_students_from_json():
    fp = open('petianos.json')
    students = json.load(fp)
    for student in students:
        create_student(student['name'], BOOLEAN[int(student['drink_coffee'])], student['entrou'], student['saiu'])
    print("\n\n\nOs Petianos obtidos do arquivo json foram criados com sucesso!\n\n")
def create_typed_student():
    name = input("Digite o nome do petiano: ")
    drink_coffee = get_int_value("Bebe café? Digite 0 para não e 1 para sim")
    entrou = input("Insira a data de entrada\nformato dd/mm/aaaa\n>>> ")
    saiu = '1/1/2020'
    create_student(name, BOOLEAN[drink_coffee], entrou, saiu)
    print("O Petiano digitado foi criado com sucesso!")

FUNCS_READ_STUDENTS = {1: create_typed_student, 2: create_students_from_json}
def create_student_view():
    print("OPÇÕES:\n1 - Digitar estudante\n2 - Ler arquivo json\n")
    number = get_int_value('>>> ')
    FUNCS_READ_STUDENTS[number]()

def create_payment_view():
    number = get_option_number(list_students, 'estudante')
    value = get_int_value("Qual o valor pago?")
    student = get_student(number)
    print("Inserindo pagamentos para " + student.name)
    insert_payment(student, value)

def list_students_view():
    list_students()
    input("Pressione Enter para voltar ao menu principal\n\n>>> ")

def historic():
    entrances = get_entrances()
    um_mes_atras = datetime.datetime.now()-datetime.timedelta(days=30)
    antigos = [entrance for entrance in entrances if entrance.created < um_mes_atras]
    atuais = [entrance for entrance in entrances if entrance.created >= um_mes_atras]
    saldo_antigo = sum([e.value for e in antigos])
    print("Extrato\n\nSaldo Anterior:", saldo_antigo)
    print("Moviemntação:\n")
    for entrance in atuais:
        print(entrance.value, entrance.description)
    saldo_atual = sum([e.value for e in atuais]) + saldo_antigo
    print("_____________________________\nSaldo atual: ", saldo_atual)
    input("Aperte enter para continuar:\n>>> ")
def create_entrances_view(signal, texto):
    description = input("Insira a descrição da "+texto.upper()+":\n>>> ")
    value = get_float_value("Insira o valor da "+texto.upper()+":\n>>> ")*signal
    create_entrances(value, description)
    
def create_entrances_in():
    create_entrances_view(1, 'entrada')
def create_entrances_out():
    create_entrances_view(-1, 'saida')


def export_debtors_to_excel():
    import pandas as pd
    students = get_all_students()
    names = []
    debt_names = []
    values = []
    for student in students:
        specific_debts = get_specifc_debts_to_pay(student)
        for debt in specific_debts:
            names.append(student.name)
            debt_names.append(debt.description)
            values.append(debt.value)
        debts = get_debts_to_pay(student)
        for debt in debts:
            n_penalties = get_n_penalties(debt)
            penalties = debt.penalty*n_penalties
            total = penalties + debt.value
            names.append(student.name)
            debt_names.append(str(debt))
            values.append(total)
    df = pd.DataFrame({'NOME': names, 'DESCRIÇÃO': debt_names, 'VALOR':values})
    df2 = pd.DataFrame({'NOME': names, 'VALOR':values})
    df2 = df2.groupby('NOME').sum()
    writer = pd.ExcelWriter('devedores.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name="detalhe")
    df2.to_excel(writer, sheet_name="resumo")
    writer.sheets['detalhe'].set_column('B:B', 50)
    writer.sheets['detalhe'].set_column('C:C', 16)
    writer.sheets['resumo'].set_column('A:A', 20)
    writer.save()
'''