from django.contrib import admin
from expenses.models import *

# Register your models here.

admin.site.register(Employee)
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(EmployeeSalaryAdjustment)

class WorkDayAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('date',)}


admin.site.register(WorkDay, WorkDayAdmin)