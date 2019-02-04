from django.contrib import admin
from expenses.models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(EmployeeSalaryAdjustment)
admin.site.register(File)
admin.site.register(ConstructionDivision)
admin.site.register(Expense)

class ConstructionDivisionInline(admin.TabularInline):
    model = ConstructionDivision

class ExpenseInline(admin.TabularInline):
    model = Expense

class FileInline(admin.TabularInline):
    model = File
    exclude = ('expense',)

class FileAdmin(admin.ModelAdmin):
    inlines = [
        FileInline,
    ]

class WorkDayAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('date',)}
    inlines = [
        FileInline,
        ConstructionDivisionInline,
        ExpenseInline,
    ]

class EmployeeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(WorkDay, WorkDayAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Project, ProjectAdmin)