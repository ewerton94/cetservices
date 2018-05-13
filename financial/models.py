from django.db import models
import datetime

DEBT_TYPES = {'1': "IPC", '2': "Café", '3': "Outro"}

class Student(models.Model):
    """
    Classe que representa a tabela Petiano
    """
    name = models.CharField(max_length=300)
    drink_coffee = models.BooleanField()
    get_in = models.DateTimeField()
    get_out = models.DateTimeField()
    email = models.CharField(max_length=300)
    def __str__(self):
        return self.name

class Entrance(models.Model):
    """
    Classe que representa a tabela Fluxo de Entrada e Saída
    """
    description = models.CharField(max_length=1000)
    value = models.FloatField()
    created = models.DateTimeField(default=datetime.datetime.now)
    def __str__(self):
        return self.description + str(self.value)

class DebtInfo(models.Model):
    """
    Classe que representa os débitos
    """
    month = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    type = models.CharField(max_length=1, choices=DEBT_TYPES.items())
    value = models.IntegerField()
    penalty = models.IntegerField()
    def __str__(self):
        return "%s ref. %i/%i"%(DEBT_TYPES[self.type], self.month, self.year)

class Debt(models.Model):
    """
    Classe que representa os débitos
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    debt_info = models.ForeignKey(DebtInfo, on_delete=models.CASCADE)
    value = models.IntegerField()
    paid = models.BooleanField()
    exemption = models.BooleanField()

class Credit(models.Model):
    """
    Classe que representa os pessoas que tem crédito
    """
    value = models.FloatField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
