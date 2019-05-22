from django.contrib import admin

from expenses.models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(EmployeeSalaryAdjustment)
admin.site.register(File)
admin.site.register(SubContractorProject)

class FileInline(admin.StackedInline):
    model = File

class ExpenseInline(admin.StackedInline):
    model = Expense

class EmployeeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class WorkDayInline(admin.StackedInline):
    model = WorkDay

class SubContractorPaymentInline(admin.StackedInline):
    model = SubContractorPayment

class SubContractorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class SubContractorProjectInline(admin.StackedInline):
    model = SubContractorProject

class DayAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('date',)}
    inlines = [
        WorkDayInline,
        ExpenseInline,
        SubContractorPaymentInline,
        FileInline,
    ]

admin.site.register(WorkDay)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Expense)
admin.site.register(Day, DayAdmin)
admin.site.register(SubContractorPayment)
admin.site.register(SubContractor, SubContractorAdmin)