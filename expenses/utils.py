import datetime

from expenses.models import *

def assign_alcides_to_work_day(date_start, date_end):
    if abs((datetime.strptime(date_end, '%Y-%m-%d') - datetime.strptime(date_start, '%Y-%m-%d')).days) is not 14:
        raise Exception('Date span must be 2 weeks')
    days = Day.objects.filter(date__gte=date_start, date__lte=date_end)
    alcides = Employee.objects.get(slug='alcides', foreman=True)
    for day in days:
        work_days = day.workday_set.all()
        total_work_days = len(work_days)
        for work_day in work_days:
            try:
                work_day.employee.get(slug=alcides.slug)
                raise Exception('Already assigned')
            except:
                work_day.employee.add(alcides)
                calculated_pay = EmployeeCalculatedPay.objects.create(employee = alcides, amount = 1/total_work_days * alcides.base_salary)
                work_day.employee_calculated_salary.add(calculated_pay)
                work_day.save()
