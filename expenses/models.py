import random

import googlemaps
from django.db import models
from django.template.defaultfilters import slugify

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

def geocode(address):
    # google maps client set up
    google_maps_api_key = 'AIzaSyDCd2Zzq_FCPUagE4Plp-mNbvIJEJgY9Dg'
    gmaps = googlemaps.Client(key=google_maps_api_key)
    geocode_result = gmaps.geocode(address)

    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']

    return lat, lng


class Client(models.Model):
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=400)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.lat is None or self.lng is None:
            self.lat, self.lng = geocode(self.address)
        super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.address

class Employee(models.Model):
    name = models.CharField(max_length=200)
    base_salary = models.IntegerField(blank=True, null=True)

    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class EmployeeSalaryAdjustment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return str(self.employee) + ' ' + str(self.amount)

class File(models.Model):
    file = models.FileField(upload_to='attachments')

    def __str__(self):
        return str(self.file)

class WorkDay(models.Model):
    description = models.TextField()
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ManyToManyField(Employee, blank=True)
    employee_salary_adjustment = models.ManyToManyField(EmployeeSalaryAdjustment, blank=True)
    file = models.ManyToManyField(File, blank=True)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        try:
            try_slug = WorkDay.objects.get(slug=self.slug)
            if self.pk is None:
                self.slug = self.slug + '-' + slugify(self.project.name)
            else:
            #hacked if someone manually changes slug of existing model to make it with random #
                if try_slug.pk != self.pk:
                    self.slug = self.slug + '-' + str(random.randint(1,9999)*5)
        except:
            pass
        super(WorkDay, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.date) + ' (' + str(self.project.name) + ')'

