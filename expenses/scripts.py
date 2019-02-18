from expenses.models import *

def one_off_work_day_to_day():
    work_days = WorkDay.objects.all()

    for work_day in work_days:
        try:
            day = Day.objects.get(date = work_day.date)
        except:
            day = Day.objects.create(date = work_day.date, slug=work_day.date)

        for expense in work_day.expense_set.all():
            expense.day = day
            expense.project = work_day.project
            try:
                expense.division_choice = work_day.construction_division.division_choice
            except:
                pass
            expense.save()

        for file in work_day.file_set.all():
            file.day = day
            file.project = work_day.project
            file.save()

        try:
            work_day.division_choice = work_day.construction_division.division_choice
        except:
            pass

        if work_day.day is None:
            work_day.day = day

        work_day.save()
