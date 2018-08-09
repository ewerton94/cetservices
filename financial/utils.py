from datetime import date, datetime
from models import DEBT_TYPES, Student, Entrance, Debt, Payment, Credit, SpecificDebt

def get_student(id):
    return Student.get(Student.id == id)

def list_students():
    print("OPÇÕES:")
    students = Student.select()
    for student in students:
        print(student.id, student.name, sep=' - ')

def list_debt_types():
    print("OPÇÕES:")
    for type_id in DEBT_TYPES:
        print(type_id, DEBT_TYPES[type_id], sep=' - ')

def create_debt(month, year, type, value, penalty):
    Debt.create(
        month=month,
        year=year,
        type=type,
        value=value,
        penalty=penalty
    )
    
def create_student(name, drink_coffee, entrou, saiu):
    entrou = list(map(int, entrou.split('/')))
    entrou = datetime(entrou[2], entrou[1], entrou[0])
    saiu = list(map(int, saiu.split('/')))
    saiu = datetime(saiu[2], saiu[1], saiu[0])
    Student.create(
        name=name,
        drink_coffee=drink_coffee,
        entrou=entrou,
        saiu=saiu,
        email=''
    )
    
def get_n_penalties(debt):
    date_debt = date(day=1, month=debt.month, year=debt.year)
    debts = [
        1
        for dbt in Debt.filter(Debt.type == debt.type)
        if date(day=1, month=dbt.month, year=dbt.year) > date_debt]
    return len(debts)

def create_payments(debts, student):
    for debt in debts:
        Payment.create(
            debt=debt,
            student=student,
            exemption=False
        )
def create_entrances(value, description):
    Entrance.create(
        value=value,
        description=description
    )
def get_debts_to_pay(student):
    debts = Debt.select()
    debts = [debt for debt in debts if student.entrou<datetime(debt.year, debt.month, 1)<student.saiu]
    if not student.drink_coffee:
        debts = [debt for debt in debts if debt.type==1]
    payments = Payment.filter(Payment.student_id == student.id)
    paid_debts = [pay.debt for pay in payments]
    return [debt for debt in debts if not debt in paid_debts]
def get_specifc_debts_to_pay(student):
    return SpecificDebt.filter(SpecificDebt.student_id==student.id)

def insert_payment(student, value):
    creditss = Credit.filter(Credit.student_id == student.id)
    credit = sum([crdt.value for crdt in creditss]) if creditss else 0
    value += credit
    initial_value = value
    for credit in creditss:
        credit.delete_instance()
    to_pay = get_debts_to_pay(student)
    specific_debts = get_specifc_debts_to_pay(student)
    #value_to_pay = sum([debt.value for debt in specific_debts])
    value_to_pay = sum([debt.value for debt in to_pay])
    for debt in specific_debts:
        if value>=debt.value:
            value-=debt.value
            debt.delete_instance()
            print("Foi débito específico total:",debt.value)
        else:
            debt.description = debt.description+" #Valor inicial era %i"%debt.value
            debt.value = debt.value - value
            debt.save()
            value = 0
            print("Foi débito específico parcial")
    if value >= value_to_pay:
        if value>0:
            Credit.create(value=value-value_to_pay, student=student)
        create_payments(to_pay, student)
        print("Foi pago débito geral total",value)
    else:
        ipcs = [debt for debt in to_pay if debt.type == 1]
        cafes = [debt for debt in to_pay if debt.type == 2]
        for debt in ipcs:
            n_penalties = get_n_penalties(debt)
            penalties = debt.penalty*n_penalties
            total = penalties + debt.value
            if value >= total:
                create_payments([debt,], student)
                value-=total
                print('pago ipc',debt.month,'/',debt.year,total)
        for debt in cafes:
            if value >= debt.value:
                create_payments([debt,], student)
                value-=debt.value
                print('pago café',debt.month,'/',debt.year,total)
        if value>0:
            Credit.create(value=value, student=student)
    entrance_title = "Pagamento de "+student.name+'.'
    Entrance.create(value=initial_value, description=entrance_title)
