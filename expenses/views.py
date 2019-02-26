import collections
from collections import OrderedDict
import re
from django.db.models import QuerySet, Q
from django.forms import model_to_dict
from django.http import HttpResponse, Http404
from django.template import loader

from expenses.models import Project, Client, Employee, WorkDay, Day, Expense, DIVISION_CHOICES

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

def calculate_daily_labor_spend_per_day(day):
    work_days = day.workday_set.all().order_by('date')
    total_labor_spend = 0

    for work_day in work_days:
        total_labor_spend += calculate_labor_spend_per_work_day(work_day)

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
    #check if queryset or object, if not queryset do per work day function, else do queryset function
    if isinstance(work_day, QuerySet):
        total_labor_spend = calculate_labor_spend(work_day)
    else:
        total_labor_spend = calculate_labor_spend_per_work_day(work_day)

    return total_labor_spend

def calculate_expense_spend(expenses):
    total_expense_spend = 0

    for expense in expenses:
        total_expense_spend += expense.amount

    return total_expense_spend

def calculate_total_expense_spend_per_project(project):
    expenses = Expense.objects.filter(project=project)
    return calculate_expense_spend(expenses)

def calculate_daily_expense_spend_per_day(day):
    expenses = day.expense_set.all()

    return calculate_expense_spend(expenses)

def get_day_projects(work_days, expenses, files):
    project_list = {}

    for work_day in work_days:
        try:
            project_list[work_day.project]
        except:
            project_list[work_day.project] = {}
        project_list[work_day.project]['total_labor_spend'] = 0
        project_list[work_day.project]['total_expense_spend'] = 0
        project_list[work_day.project]['work_days'] = []
        project_list[work_day.project]['project'] = work_day.project
    for expense in expenses:
        try:
            project_list[expense.project]
        except:
            project_list[expense.project] = {}
        project_list[expense.project]['total_labor_spend'] = 0
        project_list[expense.project]['total_expense_spend'] = 0
        project_list[expense.project]['expenses'] = []
        project_list[expense.project]['project'] = expense.project
    for file in files:
        try:
            project_list[file.project]
        except:
            project_list[file.project] = {}
        project_list[file.project]['total_labor_spend'] = 0
        project_list[file.project]['total_expense_spend'] = 0
        project_list[file.project]['files'] = []
        project_list[expense.project]['project'] = expense.project

    return project_list

def get_construction_divisions(expenses, work_days):
    construction_breakdown = {}

    for expense in expenses:
        key = expense.get_division_choice_display()
        try:
            construction_breakdown[key]
        except:
            construction_breakdown[key] = {}
            construction_breakdown[key]['days'] = []
            construction_breakdown[key]['number_of_days'] = 0
            construction_breakdown[key]['work_days'] = []
            construction_breakdown[key]['labor_spend'] = 0
            construction_breakdown[key]['expense_spend'] = 0
            construction_breakdown[key]['total_spend'] = 0
        construction_breakdown[key]['expense_spend'] += expense.amount
        if expense.day not in construction_breakdown[key]['days']:
            construction_breakdown[key]['days'].append(expense.day)

    for work_day in work_days:
        key = work_day.get_division_choice_display()
        try:
            construction_breakdown[key]
        except:
            construction_breakdown[key] = {}
            construction_breakdown[key]['days'] = []
            construction_breakdown[key]['number_of_days'] = 0
            construction_breakdown[key]['work_days'] = []
            construction_breakdown[key]['labor_spend'] = 0
            construction_breakdown[key]['expense_spend'] = 0
            construction_breakdown[key]['total_spend'] = 0
        construction_breakdown[key]['number_of_days'] += 1
        construction_breakdown[key]['work_days'].append(work_day)
        construction_breakdown[key]['labor_spend'] += calculate_labor_spend_per_work_day(work_day)
        if work_day.day not in construction_breakdown[key]['days']:
            construction_breakdown[key]['days'].append(work_day.day)

    for key, value in construction_breakdown.items():
        construction_breakdown[key]['total_spend'] = construction_breakdown[key]['labor_spend'] + construction_breakdown[key]['expense_spend']

    (print(construction_breakdown))

    return construction_breakdown

def index(request):
    projects = Project.objects.all()

    for project in projects:
        project.total_labor_spend = calculate_total_labor_spend_per_project(project)
        project.total_expense_spend = calculate_total_expense_spend_per_project(project)
        project.total_spend = project.total_labor_spend + project.total_expense_spend

    template = loader.get_template('index.html')
    context = {
            'project_list': projects,
    }
    return HttpResponse(template.render(context, request))

def project_detail(request, slug):
    project = Project.objects.get(slug=slug)

    project.total_labor_spend = calculate_total_labor_spend_per_project(project)

    work_days = project.workday_set.all()
    total_labor_spend = calculate_labor_spend(work_days)

    expenses = project.expense_set.all()
    total_expense_spend = calculate_expense_spend(expenses)

    total_spend = total_labor_spend + total_expense_spend

    days = OrderedDict()
    for work_day in work_days:
        if work_day.day not in days:
            days[work_day.day] = {}
            days[work_day.day]['employees'] = []
        for employee in work_day.employee.all():
            days[work_day.day]['employees'].append(employee)
    for expense in expenses:
        if expense.day not in days:
            days[expense.day] = {}

    days = sorted(days.items(), key=lambda k: k[0].date)

    construction_divisions = get_construction_divisions(expenses, work_days)

    template = loader.get_template('project_detail.html')
    context = {
            'project': project,
            'total_labor_spend': total_labor_spend,
            'total_expense_spend': total_expense_spend,
            'total_spend': total_spend,
            'days': days,
            'construction_divisions': construction_divisions,
    }
    return HttpResponse(template.render(context, request))

def workday_detail(request, slug):
    work_day = WorkDay.objects.get(slug=slug)
    template = loader.get_template('workday_detail.html')

    expenses = work_day.expense_set.all()

    daily_spend = calculate_daily_labor_spend_per_project(work_day)
    #daily_expense_spend = calculate_expense_spend_per_work_day(work_day)
    daily_total_spend = daily_spend
    #daily_total_spend = daily_spend + daily_expense_spend

    context = {
        'workday': work_day,
        'daily_spend': daily_spend,
        #'daily_expense_spend': daily_expense_spend,
        'daily_total_spend': daily_total_spend,
        'expenses': expenses,
    }

    return HttpResponse(template.render(context, request))

def day_detail(request, slug):
    day = Day.objects.get(slug=slug)
    work_days = day.workday_set.all()
    expenses = day.expense_set.all()
    files = day.file_set.all()
    template = loader.get_template('day_detail.html')
    daily_labor_spend = 0
    daily_expense_spend = 0
    daily_total_spend = 0

    day.projects = get_day_projects(work_days, expenses, files)

    for project, value in day.projects.items():
        daily_labor_spend = 0
        for work_day in work_days:
            if work_day.project == project:
                work_day.daily_labor_spend = calculate_labor_spend_per_work_day(work_day)
                day.projects[work_day.project]['work_days'].append(work_day)
                day.projects[work_day.project]['total_labor_spend'] += work_day.daily_labor_spend
                daily_labor_spend += day.projects[work_day.project]['total_labor_spend']
        for expense in expenses:
            if expense.project == project:
                day.projects[expense.project]['expenses'].append(expense)
                day.projects[expense.project]['total_expense_spend'] += expense.amount
                daily_expense_spend += day.projects[expense.project]['total_expense_spend']
        for file in files:
            if file.project == project:
                day.projects[file.project]['files'].append(file)
        day.projects[project]['daily_total_spend'] = day.projects[project]['total_labor_spend'] + day.projects[project]['total_expense_spend']
        daily_total_spend += day.projects[project]['daily_total_spend']

    context = {
        'day': day,
        'work_days': work_days,
        'expenses': expenses,
        'daily_labor_spend': daily_labor_spend,
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
        project.days = []
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
            if work_day.day not in project.days:
                project.days.append(work_day.day)

    template = loader.get_template('employee_detail.html')

    context = {
        'employee': employee,
        'projects': projects,
        'total_labor_spend': total_labor_spend,
    }

    return HttpResponse(template.render(context, request))

def calendar(request):
    template = loader.get_template('calendar.html')
    days = {}

    for day in Day.objects.all():
        days[day] = {}
        days[day]['projects'] = []
        for work_day in day.workday_set.all():
            if work_day.project not in days[day]['projects']:
                days[day]['projects'].append(work_day.project)
        for expense in day.expense_set.all():
            if expense.project not in days[day]['projects']:
                days[day]['projects'].append(expense.project)

    print(days)

    context = {
        'days': days,
    }

    return HttpResponse(template.render(context, request))

def search(request):
    project = None
    all_projects = None
    work_days = None
    expenses = None
    days = []
    total_labor_spend = 0
    total_expense_spend = 0
    total_spend = 0
    multi_work_days = None
    multi_projects = None
    construction_divisions = []

    querying_all_projects = False

    all_projects = Project.objects.all()
    for division_choice in DIVISION_CHOICES:
        construction_divisions.append(division_choice)

    all_construction_division_choices = construction_divisions

    context = {
        'all_projects': all_projects,
        'all_construction_division_choices': all_construction_division_choices,
    }

    if request.GET.get('project'):
        project_id = request.GET.get('project')
        if project_id != 'ALL':
            regexp = re.compile(r',')
            if (regexp.search(project_id)):
                res = re.split(',', project_id)
                multi_projects = []
                for r in res:
                    e_project = Project.objects.get(slug=str(r))
                    multi_projects.append(e_project)
                work_days = [Q(project=value) for value in multi_projects]
                query = work_days.pop()
                for item in work_days:
                    query |= item
                work_days = WorkDay.objects.filter(query)
                expenses = Expense.objects.filter(query)
                context['multi_projects'] = multi_projects
            else:
                project = Project.objects.get(slug=project_id)
                work_days = WorkDay.objects.filter(project=project)
                expenses = Expense.objects.filter(project=project)
                context['project'] = project

        elif project_id == 'ALL':
            context['multi_projects'] = all_projects
            work_days = WorkDay.objects.all()
            expenses = Expense.objects.all()
            querying_all_projects = True

    if request.GET.get('start_date'):
        date_start = request.GET.get('start_date')
        work_days = work_days.filter(day__date__gte=date_start)
        expenses = expenses.filter(day__date__gte=date_start)
        context['date_start'] = date_start

    if request.GET.get('end_date'):
        date_end = request.GET.get('end_date')
        work_days = work_days.filter(day__date__lte=date_end)
        expenses = expenses.filter(day__date__lte=date_end)
        context['date_end'] = date_end

    if request.GET.get('construction_divisions'):
        construction_divisions = request.GET.get('construction_divisions')
        division_choices = []
        regexp = re.compile(r',')
        res = re.split(',', construction_divisions)

        #could be several construction choices selected, so make a list of those that were clicked
        for r in res:
            division_choices.append(r)

        #delete last element because of the commas
        del division_choices[-1]

        #for context in display
        verbose_division_choices = []
        for choice in all_construction_division_choices:
            for user_choice in division_choices:
                if str(user_choice) == str(choice[0]):
                    verbose_division_choices.append(choice[1])

        #go through all work days already filtered
        for work_day in work_days:
            to_exclude = True
            #for any individual work day, get the construction division choice for that work day
            try:
                construction_division = work_day.division_choice
                #go through each of the user selected construction choices
                for division_choice in division_choices:
                    # if the construction division choice for this construction division is the same as the construction_divisions we're looking at
                    if str(construction_division) == str(division_choice):
                        # set flag to False, we're keeping this work_day
                        to_exclude = False
            except:
                pass
            if to_exclude:
                work_days = work_days.exclude(pk=work_day.pk)

        for expense in expenses:
            to_exclude = True
            try:
                construction_division = expense.division_choice
                for division_choice in division_choices:
                    if str(construction_division) == str(division_choice):
                        to_exclude = False
            except:
                pass
            if to_exclude:
                expenses = expenses.exclude(pk=expense.pk)

        #add chosen divisions to context for user display
        context['construction_divisions_queried'] = verbose_division_choices

    if work_days:
        context['work_days'] = work_days
        total_labor_spend = calculate_labor_spend(work_days)
        total_spend = total_labor_spend

        for work_day in work_days:
            if work_day.day not in days:
                days.append(work_day.day)

    if expenses:
        context['expenses'] = expenses
        total_expense_spend = calculate_expense_spend(expenses)

        total_spend += total_expense_spend

        for expense in expenses:
            if expense.day not in days:
                days.append(expense.day)

    days.sort(key=lambda r: r.date)

    context['days'] = days
    context['total_labor_spend'] = total_labor_spend
    context['total_spend'] = total_spend

    if querying_all_projects:
        for project in all_projects:
            to_exclude = False
            if not (work_days.filter(project=project) or expenses.filter(project=project)):
                to_exclude = True
            else:
                pass
            if to_exclude:
                all_projects = all_projects.exclude(pk=project.pk)
        context['multi_projects'] = all_projects

    template = loader.get_template('date_filter.html')

    return HttpResponse(template.render(context, request))
