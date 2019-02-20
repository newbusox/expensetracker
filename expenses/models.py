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

    subcontractor_project = models.ManyToManyField(SubContractorProject, blank=True)

    def __str__(self):
        return str(self.date)

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

class WorkDay(models.Model):
    description = models.TextField()
    #to delte (the date)
    date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ManyToManyField(Employee, blank=True)
    employee_salary_adjustment = models.ManyToManyField(EmployeeSalaryAdjustment, blank=True)
    slug = models.SlugField()

    division_choice = models.CharField(
        max_length=2,
        choices=DIVISION_CHOICES,
        blank=True,
        null=True,
    )

    day = models.ForeignKey(Day, on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            try_slug = WorkDay.objects.get(slug=self.slug)
            if self.pk is None:
                self.slug = self.slug + '-' + slugify(self.project.name)
                try:
                    double_try_slug = WorkDay.objects.get(slug=self.slug)
                    self.slug = self.slug + '-' + str(random.randint(1,9999)*5)
                except:
                    pass
            else:
            #hacked if someone manually changes slug of existing model to make it with random, not good longterm solution... #
                if try_slug.pk != self.pk:
                    self.slug = self.slug + '-' + str(random.randint(1,9999)*5)
        except:
            pass
        super(WorkDay, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.date) + ' (' + str(self.project.name) + ')'

class File(models.Model):
    file = models.FileField(upload_to='attachments')
    day = models.ForeignKey(Day, on_delete=models.SET_NULL, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

    # to delete
    workday = models.ForeignKey(WorkDay, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.file)

#!! delete entire class
class ConstructionDivision(models.Model):
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

    # rename to singular?
    division_choice = models.CharField(
        max_length=2,
        choices=DIVISION_CHOICES,
    )

    workday = models.OneToOneField(WorkDay, on_delete=models.CASCADE, related_name='construction_division', blank=True, null=True)
    subcontractor = models.OneToOneField(SubContractor, on_delete=models.CASCADE, related_name='construction_division', blank=True, null=True)

    def __str__(self):
        return str(self.division_choice)

class Expense(models.Model):
    amount = models.FloatField()
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='attachments', blank=True)
    day = models.ForeignKey(Day, on_delete=models.SET_NULL, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    construction_division = models.ForeignKey(ConstructionDivision, on_delete=models.CASCADE, blank=True, null=True)

    division_choice = models.CharField(
        max_length=2,
        choices=DIVISION_CHOICES,
        blank=True,
        null=True,
    )

    #!! delete foreign key
    workday = models.ForeignKey(WorkDay, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.amount)
