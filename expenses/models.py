from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Project(models.Model):
    address = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.address

class Employee(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class WorkDay(models.Model):
    description = models.TextField()
    date = models.DateField()
    project = models.ManyToManyField(Project, blank=True)
    employee = models.ManyToManyField(Employee, blank=True)

    def __str__(self):
        return str(self.date)
