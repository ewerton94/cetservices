# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
from django.db import models
import datetime
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from itertools import combinations
import threading

DEBT_TYPES = {'1': "IPC", '2': "Café", '3': "Outro"}

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, from_email, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.from_email = from_email
        threading.Thread.__init__(self)

    def run (self):
        send_mail(self.subject, self.html_content, self.from_email, self.recipient_list, fail_silently=True)

class Student(models.Model):
    """
    Classe que representa a tabela Petiano
    """
    class Meta:
        verbose_name = "PETiano"
        verbose_name_plural = "PETianos"
        ordering = ('name',)
    name = models.CharField(max_length=300)
    drink_coffee = models.BooleanField()
    get_in = models.DateTimeField()
    get_out = models.DateTimeField(null=True, blank=True)
    email = models.CharField(max_length=300)
    balance = models.FloatField(default=0.00)
    def __unicode__(self):
        return self.name
    if sys.version_info[0] >= 3: # Python 3
        def __str__(self):
            return self.__unicode__()
    else:  # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')

    

class Entrance(models.Model):
    """
    Classe que representa a tabela Fluxo de Entrada e Saída
    """
    class Meta:
        verbose_name = "Fluxo de Entrada e Saída"
        verbose_name_plural = "Fluxo de Entrada e Saída"
    description = models.CharField(max_length=1000)
    value = models.FloatField()
    created = models.DateTimeField(default=datetime.datetime.now)
    def __unicode__(self):
        return "(R$ %s)     " %str(self.value) + self.description
    if sys.version_info[0] >= 3: # Python 3
        def __str__(self):
            return self.__unicode__()
    else:  # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')

class DebtInfo(models.Model):
    """
    Classe que representa os débitos
    """
    class Meta:
        verbose_name = "Débito Geral"
        verbose_name_plural = "Débitos Gerais"
    month = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    type = models.CharField(max_length=1, choices=DEBT_TYPES.items())
    value = models.IntegerField()
    penalty = models.IntegerField()

    def __unicode__(self):
        return "%s ref. %i/%i"%(DEBT_TYPES[self.type], self.month, self.year)
    if sys.version_info[0] >= 3: # Python 3
        def __str__(self):
            return self.__unicode__()
    else:  # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')
    
    def save(self):
        super(DebtInfo, self).save()
        if self.id and Debt.objects.filter(debt_info=self).count()==0:
            for student in Student.objects.all():
                if self.type=='2' and student.drink_coffee==False:
                    continue
                get_in = timezone.datetime(student.get_in.year, student.get_in.month, student.get_in.day)
                if not student.get_out is None:
                    get_out = timezone.datetime(student.get_out.year, student.get_out.month, student.get_out.day)
                    if get_in <= timezone.datetime(self.year, self.month, 1) <= get_out:
                        Debt.objects.create(student=student, debt_info=self)
                else:
                    if get_in <= timezone.datetime(self.year, self.month, 1):
                        d = Debt(student=student, debt_info=self)       
                        d.save()             

            #send_mail('Pagamento IPC []!'%self.,mes,from_email,to_list,fail_silently=True)
        

class Debt(models.Model):
    """
    Classe que representa os débitos
    """
    class Meta:
        verbose_name = "Débito individual"
        verbose_name_plural = "Débitos Individuais"
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    debt_info = models.ForeignKey(DebtInfo, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    exemption = models.BooleanField(default=False)
    discount = models.FloatField(default=0.00)

    def save(self):
        if self.id and self.debt_info.type!='3':
            old_debt = Debt.objects.get(pk=self.id)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_list=[self.student.email,]
            if old_debt.paid==False and self.paid:
                mes = "Pagamento Realizado: %s\n\nO PET Agradece sua contribuição.\n\nAtenciosamente,\n\nComissão de Financeiro do PET Ciência e Tecnologia"%(self.debt_info.__unicode__())
                #txt = "Pagamento %s -  %s" % (self.student.name, self.debt_info.__unicode__())

                print(mes)
                print(to_list)
                EmailThread('Pagamento Total de Dívida!',mes,from_email,to_list).start()
            elif old_debt.exemption==False and self.exemption:
                mes = "Isenção realizada: %s\n\nAtenciosamente,\n\nComissão de Financeiro do PET Ciência e Tecnologia"%(self.debt_info.__unicode__())
                print(mes)
                EmailThread('Isenção de Dívida!',mes,from_email,to_list).start()
            else:
                print('N mandou email')
                #send_mail('Pagamento IPC []!'%self.,mes,from_email,to_list,fail_silently=True)
        super(Debt, self).save()


class Credit(models.Model):
    """
    Classe que representa os pessoas que tem crédito
    """
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
    id = models.AutoField(primary_key=True)
    value = models.FloatField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def get_debts_to_pay(self):
        return Debt.objects.filter(student=self.student, paid=False, exemption=False)
    
    def save(self):
        print(self.id)
        if not self.id:
            ds = self.get_debts_to_pay()
            dict_debts = {}
            for d in ds:
                dict_debts.setdefault(d.debt_info.value - d.discount + d.debt_info.penalty, []).append(d)  
            value_to_pay = sum([d.debt_info.value - d.discount + d.debt_info.penalty for d in ds])
            total = self.student.balance + self.value
            if value_to_pay != total:
                debt = dict_debts.get(total, None)
                if debt is None:
                    print('Não achou igual')
                    for i in range(2, 7):
                        keys = []
                        for key in dict_debts.keys():
                            for j in range(len(dict_debts[key])):
                                keys.append(key)
                        s = {sum(c):c for c in combinations(keys, i)}
                        print("#### Combinação  = "+str(i))
                        print(s)
                        if not s:
                            print('Finalizou procura')
                            break
                        debts = s.get(total, None)
                        if not debts is None:
                            print('Achou débitos somados iguais')
                            ds = []
                            for value in set(debts):
                                for j in range(debts.count(value)):
                                    ds.append(dict_debts[value][j])
                            break
                else:
                    ds = [debt[0],]
            debts_to_pay = sorted(sorted(sorted(sorted(ds, key=lambda x: x.id), key=lambda x: x.debt_info.type), key=lambda x:x.debt_info.year),  key=lambda x: x.debt_info.month) 
            
            if not debts_to_pay:
                self.student.balance = total
            for debt in debts_to_pay:
                if total == 0:
                    break
                total_debt = debt.debt_info.value - debt.discount + debt.debt_info.penalty
                if total >= total_debt:
                    debt.paid = True
                    debt.save()
                    Entrance.objects.create(description='Pagamento - '+str(debt.debt_info)+" por "+str(debt.student), value=total_debt)
                    total -= total_debt
                else:
                    debt.discount = debt.discount + total
                    debt.save()
                    Entrance.objects.create(description='Pagamento parcial - '+str(debt.debt_info) + ' por '+str(debt.student), value=total)
                    mes = "Pagamento parcial Realizado: %s\n\nO PET Agradece sua contribuição.\n\nAtenciosamente,\n\nComissão de Financeiro do PET Ciência e Tecnologia"%(str(debt.debt_info) + '\nValor: R$' + str(total))
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to_list=[self.student.email,]
                    EmailThread('Pagamento parcial - '+str(debt.debt_info),mes,from_email,to_list).start()
                    total = 0
        super(Credit, self).save()

    def __unicode__(self):
        return "(R$ %s)  - Pagamento por %s" %(str(self.value), str(self.student.name))
    if sys.version_info[0] >= 3: # Python 3
        def __str__(self):
            return self.__unicode__()
    else:  # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')

 