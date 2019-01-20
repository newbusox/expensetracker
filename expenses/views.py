import googlemaps
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

from expenses.models import Project, Client, Employee, WorkDay

def calculate_total_labor_spend(project):
    total_labor_spend = 0
    work_days = project.workday_set.all()

    work_days = WorkDay.objects.filter(project=project)

    for work_day in work_days:
        employees = work_day.employee.all()
        for employee in employees:
            total_labor_spend += employee.base_salary

    return total_labor_spend

def calculate_daily_labor_spend_per_project(work_day):
    labor_spend = 0

    employees = work_day.employee.all()
    for employee in employees:
        labor_spend += employee.base_salary

    return labor_spend

def calcaulte_daily_labor_spend(date):
    labor_spend = 0
    return labor_spend


def index(request):
    projects = Project.objects.all()

    for project in projects:
        project.total_labor_spend = calculate_total_labor_spend(project)

    template = loader.get_template('index.html')
    context = {
            'project_list': projects,
    }
    return HttpResponse(template.render(context, request))


def project_detail(request, slug):
    project = Project.objects.get(slug=slug)

    project.total_labor_spend = calculate_total_labor_spend(project)

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
        print(project)
        project.employee_labor_spend = 0
        project.work_days = []
        work_days = project.workday_set.all()
        for work_day in work_days:
            print(work_day)
            try:
                work_day.employee.get(id=employee.id)
                project.work_days.append(work_day)
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
