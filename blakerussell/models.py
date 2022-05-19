from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from multiselectfield import MultiSelectField
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from .apichoices import *

# Create your models here.

# Used to call Business Name & Image/Logo for print/pdf views
class SiteConfig(models.Model):
	class Meta:
		ordering = ['sitename']
	sitename = models.CharField(max_length=100, blank=True)
	logo = models.ImageField(upload_to='images', default='logo.png')
	def __str__(self):
		return str(self.sitename)

class Property(models.Model):
	class Meta:
		ordering = ['name']
	name = models.CharField(max_length=100, blank=True)
	addressfull = models.CharField(max_length=100, unique=True, blank=True)
	address = models.CharField(max_length=50, unique=True, blank=True)
	city = models.CharField(max_length=50, unique=False, blank=True)
	state = models.CharField(max_length=2, unique=False, blank=True)
	zipcode = models.CharField(max_length=10, unique=False, blank=True)
	county = models.CharField(max_length=50, unique=False, blank=True)
	yearbuilt = models.CharField(max_length=4, unique=False, blank=True)
	homesize = models.CharField(max_length=5, unique=False, blank=True)
	lotsize = models.CharField(max_length=5, unique=False, blank=True)
	bedrooms = models.CharField(max_length=4, unique=False, blank=True)
	bathrooms = models.CharField(max_length=4, unique=False, blank=True)
	latitude = models.CharField(max_length=12, unique=False, blank=True)
	longitude = models.CharField(max_length=12, unique=False, blank=True)
	last_sold_date = models.CharField(max_length=10, unique=False, blank=True)
	last_sold_price = models.CharField(max_length=15, blank=True)
	sales_price = models.CharField(max_length=15, blank=True)
	rent_price = models.CharField(max_length=15, blank=True)
	rent_growth = models.FloatField(default='2.0', max_length=15, blank=True)
	downpayment = models.IntegerField(default='20', blank=True)
	interestrate = models.FloatField(default='5.0', blank=True)
	insurancefees = models.CharField(max_length=15, blank=True)
	hoafees = models.CharField(max_length=15, blank=True)
	otherfees = models.CharField(default='0', max_length=15, blank=True)
	pmrate = models.FloatField(default='8.0', max_length=15, blank=True)
	pmfee = models.CharField(max_length=15, blank=True)
	leaserate = models.FloatField(default='3.0', max_length=15, blank=True)
	repairrate = models.FloatField(default='5.0', max_length=15, blank=True)
	vacancyrate = models.FloatField(default='6.5', blank=True)
	capexrate = models.FloatField(default='3.0', max_length=15, blank=True)
	zestimate = models.CharField(default='0', max_length=15, blank=True)
	zestimate_high = models.CharField(max_length=15, blank=True)
	zestimate_low = models.CharField(max_length=15, blank=True)
	zestimate_last_updated = models.CharField(max_length=15, blank=True)
	rentzestimate = models.CharField(max_length=15, blank=True)
	rentzestimate_high = models.CharField(max_length=15, blank=True)
	rentzestimate_low = models.CharField(max_length=15, blank=True)
	rentzestimate_last_updated = models.CharField(max_length=15, blank=True)
	yr1 = models.IntegerField(default=2003, blank=True)
	yr2 = models.IntegerField(default=2002, blank=True)
	yr3 = models.IntegerField(default=2001, blank=True)
	yr4 = models.IntegerField(default=2000, blank=True)
	yr5 = models.IntegerField(default=1999, blank=True)
	tax_rate = models.CharField(default='2', max_length=20, blank=True)
	tax_yr0 = models.CharField(default='0', max_length=15, blank=True)
	tax_yr1 = models.CharField(default='0', max_length=15, blank=True)
	tax_yr2 = models.CharField(default='0', max_length=15, blank=True)
	tax_yr3 = models.CharField(default='0', max_length=15, blank=True)
	tax_yr4 = models.CharField(default='0', max_length=15, blank=True)
	tax_yr5 = models.CharField(default='0', max_length=15, blank=True)
	appraise_rate = models.CharField(default='2', max_length=20, blank=True)
	appraise_yr0 = models.CharField(default='0', max_length=15, blank=True)
	appraise_yr1 = models.CharField(default='0', max_length=15, blank=True)
	appraise_yr2 = models.CharField(default='0', max_length=15, blank=True)
	appraise_yr3 = models.CharField(default='0', max_length=15, blank=True)
	appraise_yr4 = models.CharField(default='0', max_length=15, blank=True)
	appraise_yr5 = models.CharField(default='0', max_length=15, blank=True)
	use_code = models.CharField(max_length=50, blank=True)
	zillow_id = models.CharField(max_length=50, blank=True)
	zillow_link = models.CharField(max_length=100, blank=True)
	image_url = models.CharField(max_length=300, blank=True)
	av_livability = models.IntegerField(default=0, blank=True)
	av_crime = models.CharField(max_length=5, blank=True)
	av_cost_of_living = models.CharField(max_length=5, blank=True)
	av_schools = models.CharField(max_length=5, blank=True)
	av_employment = models.CharField(max_length=5, blank=True)
	av_housing = models.CharField(max_length=5, blank=True)
	av_user_ratings = models.CharField(max_length=5, blank=True)
	gs_name_e = models.CharField(max_length=100, blank=True)
	gs_name_m = models.CharField(max_length=100, blank=True)
	gs_name_h = models.CharField(max_length=100, blank=True)
	gs_rating_e = models.CharField(max_length=5, blank=True)
	gs_rating_m = models.CharField(max_length=5, blank=True)
	gs_rating_h = models.CharField(max_length=5, blank=True)
	owner_name = models.CharField(max_length=100, blank=True)
	occupancy_status = models.CharField(default='', max_length=100, blank=True)
	fema1 = models.CharField(default='Unknown', max_length=200, blank=True)
	fema2 = models.CharField(default='Unknown', max_length=200, blank=True)
	fema3 = models.CharField(default='Unknown', max_length=200, blank=True)
	fema4 = models.CharField(default='Unknown', max_length=200, blank=True)
	fema5 = models.CharField(default='Unknown', max_length=200, blank=True)
	notes = models.CharField(max_length=2000, blank=True)
	usersub = models.CharField(max_length=50)
	owned = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="owned", null=True,  blank=True)
	def __str__(self):
		return str(self.address) + ", " + str(self.city) + "," + str(self.state)

# Stores API store
class ApiStore(models.Model):
	class Meta:
		ordering = ['name']
	name = models.CharField(choices=API_PROVIDER, max_length=50, null=True, blank=False)
	key = models.CharField(max_length=200, null=True, blank=False)
	url = models.CharField(max_length=200, null=True, blank=False)
	def __str__(self):
		return str(self.name)
