import re
import googlemaps
from django.db.models import QuerySet, Q
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader

from expenses.models import Project, Client, Employee, WorkDay, ConstructionDivision

#work_day is not a queryset
def calculate_labor_spend_per_work_day(work_day):
    total_labor_spend = 0
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

#work_days must be queryset
def calculate_labor_spend(work_days):
    total_labor_spend = 0

    for work_day in work_days:
        total_labor_spend += calculate_labor_spend_per_work_day(work_day)

    return total_labor_spend

def calculate_total_labor_spend_per_project(project):
    work_days = WorkDay.objects.filter(project=project)
    return calculate_labor_spend(work_days)

def calculate_daily_labor_spend_per_project(work_day):
    total_labor_spend = 0
    #check if queryset or object, if not queryset do per work day fucntino, else do queryset function
    if isinstance(work_day, QuerySet):
        total_labor_spend = calculate_labor_spend(work_day)
    else:
        total_labor_spend = calculate_labor_spend_per_work_day(work_day)

    return total_labor_spend

def calculate_expense_spend_per_work_day(work_day):
    total_expense_spend = 0
    for expense in work_day.expense_set.all():
        total_expense_spend += expense.amount

    return total_expense_spend

def calculate_expense_spend(work_days):
    total_expense_spend = 0

    for work_day in work_days:
        total_expense_spend += calculate_expense_spend_per_work_day(work_day)

    return total_expense_spend

def get_construction_divisions(work_days):
    construction_breakdown = {}

    for work_day in work_days:
        construction_division = ConstructionDivision.objects.filter(workday=work_day)
        for breakdown in construction_division:
            key = breakdown.get_division_choice_display()
            try:
                construction_breakdown[key]
            except:
                construction_breakdown[key] = {}
                construction_breakdown[key]['days'] = 0
                construction_breakdown[key]['work_days'] = []
                construction_breakdown[key]['labor_spend'] = 0
                construction_breakdown[key]['expense_spend'] = 0
                construction_breakdown[key]['total_spend'] = 0
            construction_breakdown[key]['days'] += 1
            construction_breakdown[key]['work_days'].append(work_day)
            construction_breakdown[key]['labor_spend'] += calculate_labor_spend_per_work_day(work_day)
            construction_breakdown[key]['expense_spend'] += calculate_expense_spend_per_work_day(work_day)
            construction_breakdown[key]['total_spend'] = construction_breakdown[key]['labor_spend'] + construction_breakdown[key]['expense_spend']

    return construction_breakdown


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

    total_labor_spend = calculate_labor_spend(days_worked)
    total_expense_spend = calculate_expense_spend(days_worked)
    total_spend = total_labor_spend + total_expense_spend

    construction_divisions = get_construction_divisions(days_worked)

    template = loader.get_template('project_detail.html')
    context = {
            'project': project,
            'total_labor_spend': total_labor_spend,
            'total_expense_spend': total_expense_spend,
            'total_spend': total_spend,
            'days_worked': days_worked,
            'construction_divisions': construction_divisions,
    }
    return HttpResponse(template.render(context, request))

def workday_detail(request, slug):
    work_day = WorkDay.objects.get(slug=slug)
    template = loader.get_template('workday_detail.html')
    daily_spend = calculate_daily_labor_spend_per_project(work_day)
    daily_expense_spend = calculate_expense_spend_per_work_day(work_day)
    daily_total_spend = daily_spend + daily_expense_spend

    context = {
        'workday': work_day,
        'daily_spend': daily_spend,
        'daily_expense_spend': daily_expense_spend,
        'daily_total_spend': daily_total_spend,
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

def search(request, project=None, date_start=None, date_end=None):
    work_days = None
    total_labor_spend = None
    total_expense_spend = None
    multi_work_days = None
    multi_projects = None

    all_projects = Project.objects.all()

    if project and project != 'ALL':
        regexp = re.compile(r'&')
        if (regexp.search(project)):
            res = re.split('&', project)
            multi_projects = []
            for r in res:
                e_project = Project.objects.get(slug=str(r))
                multi_projects.append(e_project)

            work_days = [Q(project=value) for value in multi_projects]
            query = work_days.pop()
            for item in work_days:
                query |= item
            work_days = WorkDay.objects.filter(query).order_by('date')
        else:
            project = Project.objects.get(slug=project)
            work_days = WorkDay.objects.filter(project=project).order_by('date')
    elif project == 'ALL':
        multi_projects = all_projects
        work_days = WorkDay.objects.all().order_by('date')

    context = {
            'all_projects': all_projects,
    }

    if work_days:
        if date_start:
            work_days = work_days.filter(date__gte=date_start)
        if date_end:
            work_days = work_days.filter(date__lte=date_end)
        total_labor_spend = calculate_labor_spend(work_days)
        total_spend = total_labor_spend + calculate_expense_spend(work_days)

        context = {
            'project': project,
            'total_labor_spend': total_labor_spend,
            'total_spend': total_spend,
            'work_days': work_days,
            'date_start': date_start,
            'date_end': date_end,
        }

    if multi_projects:
        del context['project']
        context['multi_projects'] = multi_projects

    template = loader.get_template('date_filter.html')

    return HttpResponse(template.render(context, request))
