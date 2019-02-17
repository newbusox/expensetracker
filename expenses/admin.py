from django.contrib import admin

from expenses.models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(EmployeeSalaryAdjustment)
admin.site.register(File)
admin.site.register(ConstructionDivision)
admin.site.register(SubContractorProject)

class ConstructionDivisionInline(admin.TabularInline):
    sortable_field_name = 'position'
    model = ConstructionDivision

class FileInline(admin.StackedInline):
    model = File

class ExpenseInline(admin.StackedInline):
    model = Expense

class SubContractorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        ConstructionDivisionInline,
    ]

class WorkDayAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('date',)}
    inlines = [
        ConstructionDivisionInline,
        ExpenseInline,
        FileInline,
    ]

class EmployeeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(SubContractor, SubContractorAdmin)
admin.site.register(WorkDay, WorkDayAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Expense)