# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from io import BytesIO as IO
from .models import Debt, Entrance, DebtInfo, Student
from .forms import EntranceForm
from django.core.mail import send_mail
from django.conf import settings
import sys
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
    entrances = Entrance.objects.all()
    cash = round(sum([e.value for e in entrances]), 2)
    entrances = entrances.order_by('-id')[:5]
    forms = [EntranceForm,]
    students = []
    descriptions = get_debt_description()
    print(descriptions)
    for desc in descriptions:
        student = Student.objects.get(name=desc['nome'])
        student.total = desc['total']
        students.append(student)
    return render(request, 'home.html', {'entrances': entrances, 'cash': cash, 'forms': forms, 'students': students, 'BASE_URL_SITE': settings.BASE_URL_SITE})

def make_penalties(request):
    for debt_info in DebtInfo.objects.filter(type='1'):
        debt_info.penalty = debt_info.penalty + 5
        debt_info.save()
    return HttpResponseRedirect('/')


def send_email_situation(request, id):
    for student in get_debt_description():
        if int(student['id'])==int(id):
            msg = 'Olá %s, já observou como o dia está lindo? Os passaros cantam, o céu está azul e as árvores balançam. Um belo dia para pagar uma de suas dívidas, não acha? Segue abaixo a sua dívida com o PET CT: \n\n%s\n\nValor total a pagar: %.2f'%(student['nome'], student['description'], student['total'])
            send_mail(
                'Oi, Coleguinha. Mensagem pra você!!! :)',
                msg,
                settings.DEFAULT_FROM_EMAIL,
                [student['email']],
                fail_silently=False,
            )
    return HttpResponseRedirect('/')


def send_mail_to_debtors(request):
    for student in get_debt_description():
       
        msg = 'Olá %s, já observou como o dia está lindo? Os passaros cantam, o céu está azul e as árvores balançam. Um belo dia para pagar uma de suas dívidas, não acha? Segue abaixo a sua dívida com o PET CT: \n\n%s\n\nValor total a pagar: %.2f'%(student['nome'], student['description'], student['total'])
        send_mail(
            'Oi, Coleguinha. Mensagem pra você!!! :)',
            msg,
            settings.DEFAULT_FROM_EMAIL,
            [student['email']],
            fail_silently=False,
        )
    return HttpResponseRedirect('/')



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