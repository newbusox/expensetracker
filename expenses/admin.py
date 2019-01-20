from django.contrib import admin
from expenses.models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(EmployeeSalaryAdjustment)

class WorkDayAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('date',)}

class EmployeeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(WorkDay, WorkDayAdmin)
admin.site.register(Employee, EmployeeAdmin)