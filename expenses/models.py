from django.db import models
from django.template.defaultfilters import slugify


class Client(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=400)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.address

class Employee(models.Model):
    name = models.CharField(max_length=200)
    base_salary = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

class EmployeeSalaryAdjustment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return str(self.employee) + ' ' + str(self.amount)

class WorkDay(models.Model):
    description = models.TextField()
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ManyToManyField(Employee, blank=True)
    employee_salary_adjustment = models.ManyToManyField(EmployeeSalaryAdjustment, blank=True)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        try:
            WorkDay.objects.get(slug=self.slug)
            self.slug = self.slug + '-' + slugify(self.project.name)
        except:
            pass
        super(WorkDay, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.date)
