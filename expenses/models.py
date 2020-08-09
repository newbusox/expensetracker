import random

import googlemaps
from django.db import models
from django.template.defaultfilters import slugify

PLANSPERMITS = '01'
DEMOLITION = '02'
FOUNDATION = '03'
ROOFGUTTERS = '04'
EXTERIORSIDING = '05'
WINDOWS = '06'
GARAGEDRIVEWAY = '07'
FRAMING = '08'
FINISHCARPENTRY = '09'
SHEETROCKINSULATION = '10'
INTERIORPAINT = '11'
FLOORING = '12'
KITCHEN = '13'
BATHROOMS = '14'
PLUMBINGWORK = '15'
ELECTRICALWORK = '16'
HVACWORK = '17'
APPLIANCES = '18'
YARDLANDSCAPING = '19'
BASEMENTFINISHES = '20'

DIVISION_CHOICES = (
    (PLANSPERMITS, 'Plans/Permits'),
    (DEMOLITION, 'Demolition'),
    (FOUNDATION, 'Foundation'),
    (ROOFGUTTERS, 'Roof/Gutters'),
    (EXTERIORSIDING, 'Exterior/Siding'),
    (WINDOWS, 'Windows'),
    (GARAGEDRIVEWAY, 'Garage/Driveway'),
    (FRAMING, 'Framing'),
    (FINISHCARPENTRY, 'Finish Carpentry'),
    (SHEETROCKINSULATION, 'Sheetrock/Insulation'),
    (INTERIORPAINT, 'Interior Paint'),
    (FLOORING, 'Flooring'),
    (KITCHEN, 'Kitchen'),
    (BATHROOMS, 'Bathrooms'),
    (PLUMBINGWORK, 'Plumbing Work'),
    (ELECTRICALWORK, 'Electrical Work'),
    (HVACWORK, 'HVAC Work'),
    (APPLIANCES, 'Appliances'),
    (YARDLANDSCAPING, 'Yard/Landscaping'),
    (BASEMENTFINISHES, 'Basement Finishes'),
)

WEEKLY = '01'
BIWEEKLY = '02'
SEMIMONTHLY = '03'
MONTHLY = '04'
DAILY = '05'

PAYPERIOD_CHOICES = (
    (WEEKLY, 'Weekly'),
    (BIWEEKLY, 'Bi-Weekly'),
    (SEMIMONTHLY, 'Semi-Monthly'),
    (MONTHLY, 'Monthly'),
    (DAILY, 'Daily'),
)

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

class SubContractor(models.Model):
    name = models.CharField(max_length=200)
    ein_number = models.CharField(max_length=200, blank=True, null=True)
    license_number = models.CharField(max_length=200, blank=True, null=True)

    main_contact = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=200, blank=True, null=True)

    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class SubContractorProject(models.Model):
    description = models.TextField()
    price = models.FloatField()

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    subcontractor = models.ForeignKey(SubContractor, on_delete=models.CASCADE)

    division_choice = models.CharField(
        max_length=2,
        choices=DIVISION_CHOICES,
        blank=True,
        null=True,
    )

    def __str__(self):
        return str(self.subcontractor.name) + ' | ' + str(self.project.name) + ' | ' + str(self.description)


class Day(models.Model):
    date = models.DateField(unique=True)
    slug = models.SlugField()

    def __str__(self):
        return str(self.date)

class SubContractorPayment(models.Model):
    amount = models.FloatField()
    subcontractor_project = models.ForeignKey(SubContractorProject, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.subcontractor_project) + ' | ' + str(self.amount) + ' | ' + str(self.day)

class SubContractorProjectDay(models.Model):
    description = models.TextField(blank=True, null=True)
    subcontractor_project = models.ForeignKey(SubContractorProject, on_delete=models.CASCADE)

    division_choice = models.CharField(
        max_length=2,
        choices=DIVISION_CHOICES,
    )

    day = models.ForeignKey(Day, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '(' + str(self.subcontractor_project.subcontractor) + ')'

class Income(models.Model):
    amount = models.FloatField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

class Employee(models.Model):
    name = models.CharField(max_length=200)
    base_salary = models.FloatField(blank=True, null=True)

    salaried = models.BooleanField(blank=True, null=True)
    foreman = models.BooleanField(blank=True, null=True)

    pay_period = models.CharField(
        max_length=2,
        choices=PAYPERIOD_CHOICES,
        blank=True,
        null=True
    )

    daily_pay = models.FloatField(blank=True, null=True, editable=False)

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.daily_pay:
            if self.pay_period == '05':
                self.daily_pay = self.base_salary
            elif self.pay_period == '04':
                self.daily_pay = self.base_salary/30
            elif self.pay_period == '03':
                self.daily_pay = self.base_salary/15
            elif self.pay_period == '02':
                self.daily_pay = self.base_salary/14
            elif self.pay_period == '01':
                self.daily_pay = self.base_salary/7
            print(self.daily_pay)
        super(Employee, self).save(*args, **kwargs)

    def __str__(self):
        return self.name + ' (' + ('Not Salaried', 'Salaried')[self.salaried==True] +  '| ' + ('Laborer', 'Foreman')[self.foreman==True] + ')'

class EmployeeSalaryAdjustment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return str(self.employee) + ' ' + str(self.amount)

class EmployeeCalculatedPay(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return str(self.employee) + ' calculated pay: ' + str(self.amount)

class WorkDay(models.Model):
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ManyToManyField(Employee, blank=True)
    employee_salary_adjustment = models.ManyToManyField(EmployeeSalaryAdjustment, blank=True)
    employee_calculated_salary = models.ManyToManyField(EmployeeCalculatedPay, blank=True, editable=False)

    division_choice = models.CharField(
        max_length=2,
        choices=DIVISION_CHOICES,
    )

    day = models.ForeignKey(Day, on_delete=models.SET_NULL, blank=True, null=True)
    def __str__(self):
        return '(' + str(self.project.name) + ')'

class File(models.Model):
    file = models.FileField(upload_to='attachments')
    day = models.ForeignKey(Day, on_delete=models.SET_NULL, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.file)

class Expense(models.Model):
    amount = models.FloatField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='attachments', blank=True)
    day = models.ForeignKey(Day, on_delete=models.SET_NULL, blank=True, null=True)

    division_choice = models.CharField(
        max_length=2,
        choices=DIVISION_CHOICES,
    )

    def __str__(self):
        return str(self.amount)
