from datetime import datetime

from expenses.models import *

def assign_alcides_to_work_day(date_start, date_end):
    if abs((datetime.strptime(date_end, '%Y-%m-%d') - datetime.strptime(date_start, '%Y-%m-%d')).days) is not 14:
        raise Exception('Date span must be 2 weeks')
    days = Day.objects.filter(date__gte=date_start, date__lte=date_end)
    alcides = Employee.objects.get(slug='alcides', foreman=True)
    work_day_count = 0
    for day in days:
        work_days = day.workday_set.all()
        for work_day in work_days:
            work_day_count += 1
    for day in days:
        work_days = day.workday_set.all()
        for work_day in work_days:
            try:
                work_day.employee.get(slug=alcides.slug)
                pass
            except:
                work_day.employee.add(alcides)
                calculated_pay = EmployeeCalculatedPay.objects.create(employee = alcides, amount = 1/work_day_count * alcides.base_salary)
                work_day.employee_calculated_salary.add(calculated_pay)
                work_day.save()
