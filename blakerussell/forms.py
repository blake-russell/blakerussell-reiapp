from django import forms
from multiselectfield import MultiSelectField
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.contrib.auth.models import User
from django.core.validators	import RegexValidator
from .models import *

# Create your forms here.

class PropertyFormSub(forms.ModelForm):
	class Meta:
		model = Property
		fields = ('addressfull',)
	#addressfull = forms.CharField(label="Full Address:", help_text="See example below...", validators=[RegexValidator(r'^([0-9]{1,5}\s)([A-Za-z]{1,}(\#\s|\s\#|\s\#\s|\s)){1,5}([A-Za-z]{1,}\,|[0-9]{1,}\,)(\s[a-zA-Z]{1,}\,|[a-zA-Z]{1,}\,)(\s[a-zA-Z]{2}\s|[a-zA-Z]{2}\s)([0-9]{5})$', message='Input does not meet appropriate address format. Please see example below.')])
	addressfull = forms.CharField(label="Full Address:", help_text="See example below...")

class PropertyFormNotes(forms.ModelForm):
	class Meta:
		model = Property
		fields = ('notes',)
	notes = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        required=False,
    )

class PropertyForm(forms.ModelForm):
	class Meta:
		model = Property
		fields = ('addressfull', 'address','city', 'state', 'zipcode', \
			'sales_price', 'rent_price', 'rent_growth', 'downpayment', \
			'interestrate', 'tax_yr0', 'pmrate', 'leaserate', 'hoafees', \
			'insurancefees', 'repairrate', 'capexrate', 'otherfees', 'tax_rate', \
			'appraise_rate', 'vacancyrate', 'image_url', 'owned', 'notes')
	addressfull = forms.CharField(label="Full Address:")
	address = forms.CharField(label="Address:")
	city = forms.CharField(label="City:")
	state = forms.CharField(label="State:")
	zipcode = forms.CharField(label="Zipcode:")
	sales_price = forms.CharField(label="Actual Sales Price:", required=False)
	rent_price = forms.CharField(label="Estimated Rent:", required=False)
	rent_growth = forms.CharField(label="Estimated Rent Growth:", required=False)
	downpayment = forms.IntegerField(label="Downpayment %:", help_text="Enter full number such as 20 for 20%.", required=True)
	interestrate = forms.FloatField(label="Interest Rate on Loan:", help_text="Enter full number such as 5 for 5%.", required=True)
	tax_yr0 = forms.CharField(label="Yearly Tax Amount:", help_text="Ignores calculated rates if entered.", required=False)
	pmrate = forms.CharField(label="Monthly Property Management Rate:", help_text="Enter full number such as 8 for 8%.", required=False)
	leaserate = forms.CharField(label="Monthly Lease Rate:", help_text="Enter full number such as 4 for 4%.", required=False)
	hoafees = forms.CharField(label="Yearly HOA Fee:", required=False)
	insurancefees = forms.CharField(label="Yearly Insurance Premium:", help_text="Ignores calculated rates if entered.", required=False)
	repairrate = forms.CharField(label="Monthly Maintenance Rate:", help_text="Enter full number such as 3 for 3%.", required=False)
	capexrate = forms.CharField(label="Monthly CapEX Rate:", help_text="Enter full number such as 4 for 4%.", required=False)
	otherfees = forms.CharField(label="Other Monthly Fee(s):", required=False)
	tax_rate = forms.CharField(label="Avg. YoY Tax Rate:", help_text="Average YoY increase in tax amount.", required=False)
	appraise_rate = forms.CharField(label="Avg. YoY Appreciation:", help_text="Average YoY increase in property value.", required=False)
	vacancyrate = forms.FloatField(label="Vacancy Rate:", help_text="Enter full number such as 6 for 6%.", required=True)
	image_url = forms.CharField(label="Image URL:", required=False)
	owned = forms.ModelChoiceField(label="Owner:", help_text="Owner of Property.", queryset=User.objects.all(), required=False)
	notes = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        required=False,
        help_text='Write down notes for this property.'
    )

class ApiStoreForm(forms.ModelForm):
	class Meta:
		model = ApiStore
		fields = ('name', 'key', 'url')
	name = forms.ChoiceField(label="API Endpoint Name:", help_text="Choose a provider.", choices=API_PROVIDER, required=True)
	key = forms.CharField(label="API Key/Token:", help_text="API Key or Token.", required=True)
	url = forms.CharField(label="Endpoint Base URL:", help_text="The base endpoint URL.", required=True)