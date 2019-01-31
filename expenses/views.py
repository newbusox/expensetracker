import googlemaps
from django.db.models import QuerySet
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

from expenses.models import Project, Client, Employee, WorkDay

#work_days must be queryset
def calculate_labor_spend(work_days):
    total_labor_spend = 0

    for work_day in work_days:
        employees = work_day.employee.all()
        salary_adjustments = work_day.employee_salary_adjustment.all()
        for employee in employees:
            # if there is a salary adjust in the day, see if it matches the employee we're on
            # if so, adjust total labor spend by that amount; if not, just add in base salary
            try:
                salary_adjustment = salary_adjustments.get(employee_id=employee.id)
                total_labor_spend += employee.base_salary + int(salary_adjustment.amount)
            except:
                total_labor_spend += employee.base_salary

    return total_labor_spend

def calculate_total_labor_spend_per_project(project):
    work_days = WorkDay.objects.filter(project=project)
    return calculate_labor_spend(work_days)

def calculate_daily_labor_spend_per_project(work_day):
    #check if queryset or object, if not queryset, get a queryset by .filter
    if isinstance(work_day, QuerySet):
        pass
    else:
        work_day = WorkDay.objects.filter(id=work_day.id)

    return calculate_labor_spend(work_day)

def index(request):
    projects = Project.objects.all()
    work_days = WorkDay.objects.all().order_by('date')

    for project in projects:
        project.total_labor_spend = calculate_total_labor_spend_per_project(project)

    template = loader.get_template('index.html')
    context = {
            'project_list': projects,
            'work_days': work_days,
    }
    return HttpResponse(template.render(context, request))


def project_detail(request, slug):
    project = Project.objects.get(slug=slug)

    project.total_labor_spend = calculate_total_labor_spend_per_project(project)

    days_worked = project.workday_set.all().order_by('date')

    template = loader.get_template('project_detail.html')
    context = {
            'project': project,
            'days_worked': days_worked,
    }
    return HttpResponse(template.render(context, request))

def workday_detail(request, slug):
    workday = WorkDay.objects.get(slug=slug)
    template = loader.get_template('workday_detail.html')
    daily_spend = calculate_daily_labor_spend_per_project(workday)

    context = {
        'workday': workday,
        'daily_spend': daily_spend,
    }

    return HttpResponse(template.render(context, request))

def employee_detail(request,slug):
    employee = Employee.objects.get(slug=slug)
    total_labor_spend = 0

    projects = Project.objects.all()

    for project in projects:
        project.employee_labor_spend = 0
        project.work_days = []
        work_days = project.workday_set.all()
        for work_day in work_days:
            salary_adjustments = work_day.employee_salary_adjustment.all()
            try:
                work_day.employee.get(id=employee.id)
                project.work_days.append(work_day)
                try:
                    salary_adjustment = salary_adjustments.get(employee_id=employee.id)
                    project.employee_labor_spend += employee.base_salary + int(salary_adjustment.amount)
                    total_labor_spend += employee.base_salary + int(salary_adjustment.amount)
                except:
                    project.employee_labor_spend += employee.base_salary
                    total_labor_spend += employee.base_salary
            except:
                pass

    template = loader.get_template('employee_detail.html')

    context = {
        'employee': employee,
        'projects': projects,
        'total_labor_spend': total_labor_spend,
    }

    return HttpResponse(template.render(context, request))

def calendar(request):
    template = loader.get_template('calendar.html')
    workdays = WorkDay.objects.all()
    context = {
        'work_days': workdays,
    }

    return HttpResponse(template.render(context, request))

def date_filter(request, project=None, date_start=None, date_end=None):
    work_days = None
    total_labor_spend = None
    all_projects = Project.objects.all()

    if project:
        project = Project.objects.get(slug=project)
        work_days = WorkDay.objects.filter(project=project)
    if date_start:
        work_days = work_days.filter(date__gte=date_start)
    if date_end:
        work_days = work_days.filter(date__lte=date_end)
    if work_days:
        work_days.order_by('date')
        total_labor_spend = calculate_labor_spend(work_days)

    template = loader.get_template('date_filter.html')

    context = {
        'all_projects': all_projects,
        'project': project,
        'total_labor_spend': total_labor_spend,
        'work_days': work_days,
        'date_start': date_start,
        'date_end': date_end,
    }

    return HttpResponse(template.render(context, request))
