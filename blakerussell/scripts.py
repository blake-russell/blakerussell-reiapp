from xml.etree import cElementTree as ElementTree
from django.core.exceptions import ObjectDoesNotExist
from blakerussell.models import *
from .rates import *
from .lists import *
from bs4 import BeautifulSoup
from lxml import html
import re
import random
import requests
import datetime

### REI Calculation Scripts

def DownPayment(price, down):
	downpercent = float(down)/100
	downpayment = float(price) * downpercent
	return int(downpayment)

def ClosingCosts(price, state):
	closingcost = float(price) * closing_cost_rates[state]
	return int(closingcost)

def InsuranceRates(price, state):
	insurancerate = float(price) * average_insurance_rates[state]
	return int(insurancerate)

def InsurancePremiums(state):
	insurancepremium = average_insurance_premiums[state]
	return int(insurancepremium)

def ConvertStateName(abbr):
	for state in state_name_list:
		if abbr == state:
			return state_name_list[state]

def StateTaxRate(state):
	taxrate = float(income_tax_rates[state])
	return float(taxrate)

def CalcMortgagePayment(price, down, rate):
	principal = float(price) - float(down)
	n = 360 # 360 months = 30 years
	r = (float(rate) / 100) / 12  # decimal monthly interest rate from APR
	MonthlyPayment = (r * principal * ((1+r) ** n)) / (((1+r) ** n) - 1)
	return round(float(MonthlyPayment))

def CalcPrinciple(rate, nper, pmt, pv):
    """
    rate    - annual interest rate
    nper    - # of periodic payments
    pmt     - monthly payment
    pv      - present value (principal loan amount)

    r1 = (1 + interest_rate) - will be used a few times below
    """
    r1 = 1 + rate
    return round(float(pv * r1**nper - pmt * (r1**nper -1) / rate))

def PropViewCalc1yr(prop):
	propview1yr = {}

	propview1yr['vacancyfactor'] = round(float(prop.rent_price) * (float(prop.vacancyrate)/100))
	propview1yr['expectedrent1m'] = round(float(prop.rent_price) - float(propview1yr['vacancyfactor']))
	propview1yr['expectedrent1y'] = round(float(propview1yr['expectedrent1m'] *12))

	if prop.tax_yr1 == '':
		taxamount = '0'
	elif prop.tax_yr0 == '':
		taxamount = prop.tax_yr1
	else:
		taxamount = prop.tax_yr0
	
	tax_rate = (float(prop.tax_rate)/100)
	propview1yr['propertytaxes1y'] = round(float(taxamount) + (float(taxamount) * float(tax_rate)))
	propview1yr['propertytaxes1m'] = round((float(taxamount) + (float(taxamount) * float(tax_rate)))/12)

	appraise_rate = (float(prop.appraise_rate)/100)
	propview1yr['propertyvalue'] = round(float(prop.sales_price) + (float(prop.sales_price) * float(appraise_rate)))

	if prop.pmfee == '':
		propview1yr['pmfee1m'] = round(float(propview1yr['expectedrent1m']) * (prop.pmrate/100))
		propview1yr['pmfee1y'] = round((float(propview1yr['expectedrent1m']) * (prop.pmrate/100))*12)
	elif prop.pmfee:
		propview1yr['pmfee1m'] = float(prop.pmfee)
		propview1yr['pmfee1y'] = round(float(prop.pmfee)*12)

	propview1yr['leasefee1m'] = round(float(propview1yr['expectedrent1m']) * (prop.leaserate/100))
	propview1yr['leasefee1y'] = round((float(propview1yr['expectedrent1m']) * (prop.leaserate/100))*12)

	try:
		propview1yr['hoafee1m'] = round(float(prop.hoafees)/12)
		propview1yr['hoafee1y'] = round(float(prop.hoafees))
	except:
		propview1yr['hoafee1m'] = 0.0
		propview1yr['hoafee1y'] = 0.0

	if prop.insurancefees == '':
		insuracefee_1yr = InsurancePremiums(prop.state)
	elif prop.insurancefees:
		insuracefee_1yr = prop.insurancefees
	else:
		insuracefee_1yr = 0.0

	propview1yr['insurancefee1m'] = round(float(insuracefee_1yr)/12)
	propview1yr['insurancefee1y'] = round(float(insuracefee_1yr))

	propview1yr['otherfee1m'] = float(prop.otherfees)
	propview1yr['otherfee1y'] = float(propview1yr['otherfee1m'] * 12)

	propview1yr['nonrepairfee1y'] = round(float(propview1yr['pmfee1y'] + propview1yr['leasefee1y'] + propview1yr['hoafee1y'] + propview1yr['insurancefee1y'] + propview1yr['otherfee1y']))

	propview1yr['repairfee1m'] = round(float(propview1yr['expectedrent1m']) * (prop.repairrate/100))
	propview1yr['repairfee1y'] = round((float(propview1yr['expectedrent1m']) * (prop.repairrate/100))*12)

	propview1yr['opex1m'] = float(propview1yr['propertytaxes1m'] + propview1yr['pmfee1m'] + \
								propview1yr['leasefee1m'] + propview1yr['hoafee1m'] + propview1yr['insurancefee1m'] + \
								propview1yr['repairfee1m'])

	propview1yr['opex1y'] = float(propview1yr['propertytaxes1y'] + propview1yr['pmfee1y'] + \
								propview1yr['leasefee1y'] + propview1yr['hoafee1y'] + propview1yr['insurancefee1y'] + \
								propview1yr['repairfee1y'])

	propview1yr['noi1m'] = round(float(propview1yr['expectedrent1m'] - propview1yr['opex1m']))
	propview1yr['noi1y'] = round(float(propview1yr['expectedrent1m'] * 12) - float(propview1yr['opex1y']))

	propview1yr['capex1m'] = round(float(propview1yr['expectedrent1m']) * (prop.capexrate / 100))
	propview1yr['capex1y'] = round((float(propview1yr['expectedrent1m']) * (prop.capexrate / 100))*12)

	propview1yr['unlevcf1m'] = round(float(propview1yr['noi1m'] - propview1yr['capex1m']))
	propview1yr['unlevcf1y'] = round(float(propview1yr['noi1y'] - propview1yr['capex1y']))

	# need to add mortgage calculation
	propview1yr['mortgage1m'] = CalcMortgagePayment(prop.sales_price, DownPayment(prop.sales_price, prop.downpayment), prop.interestrate)
	propview1yr['mortgage1y'] = float(propview1yr['mortgage1m'] * 12)
	propview1yr['original_principle'] = float(prop.sales_price) - float(DownPayment(prop.sales_price, prop.downpayment))
	propview1yr['principal'] = CalcPrinciple(float(((prop.interestrate)/100)/12), 12, propview1yr['mortgage1m'], propview1yr['original_principle'])
	propview1yr['equity'] = propview1yr['propertyvalue'] - propview1yr['principal']

	propview1yr['totalnetcf1m'] = round(float(propview1yr['unlevcf1m'] - propview1yr['mortgage1m']))
	propview1yr['totalnetcf1y'] = round(float(propview1yr['unlevcf1y'] - propview1yr['mortgage1y']))

	propview1yr['posttaxncf'] = round((propview1yr['totalnetcf1y']) - (propview1yr['totalnetcf1y'] * StateTaxRate(prop.state)))

	propview1yr['posttaxncfplusequity'] = propview1yr['posttaxncf'] + propview1yr['equity']

	return propview1yr


def PropViewCalc5yr(prop, propview1yr):
	propview5yr = {}
	rent_growth = float(prop.rent_growth / 100)
	propview5yr['expectedrent1y'] = propview1yr['expectedrent1y']
	propview5yr['expectedrent2y'] = round((propview5yr['expectedrent1y'] * rent_growth) + propview5yr['expectedrent1y'])
	propview5yr['expectedrent3y'] = round((propview5yr['expectedrent2y'] * rent_growth) + propview5yr['expectedrent2y'])
	propview5yr['expectedrent4y'] = round((propview5yr['expectedrent3y'] * rent_growth) + propview5yr['expectedrent3y'])
	propview5yr['expectedrent5y'] = round((propview5yr['expectedrent4y'] * rent_growth) + propview5yr['expectedrent4y'])
	propview5yr['expectedrent'] = round(propview5yr['expectedrent1y'] + propview5yr['expectedrent2y'] + propview5yr['expectedrent3y'] + \
								propview5yr['expectedrent4y'] + propview5yr['expectedrent5y'])

	tax_growth = float(float(prop.tax_rate) / 100)
	propview5yr['propertytaxes1y'] = propview1yr['propertytaxes1y']
	propview5yr['propertytaxes2y'] = round((propview5yr['propertytaxes1y'] * tax_growth) + propview5yr['propertytaxes1y'])
	propview5yr['propertytaxes3y'] = round((propview5yr['propertytaxes2y'] * tax_growth) + propview5yr['propertytaxes2y'])
	propview5yr['propertytaxes4y'] = round((propview5yr['propertytaxes3y'] * tax_growth) + propview5yr['propertytaxes3y'])
	propview5yr['propertytaxes5y'] = round((propview5yr['propertytaxes4y'] * tax_growth) + propview5yr['propertytaxes4y'])
	propview5yr['propertytaxes'] = round(propview5yr['propertytaxes1y'] + propview5yr['propertytaxes2y'] + propview5yr['propertytaxes3y'] + \
								propview5yr['propertytaxes4y'] + propview5yr['propertytaxes5y'])

	appraise_rate = (float(prop.appraise_rate)/100)
	propview5yr['propertyvalue1y'] = propview1yr['propertyvalue']
	propview5yr['propertyvalue2y'] = round(float(propview5yr['propertyvalue1y']) + (float(propview5yr['propertyvalue1y']) * float(appraise_rate)))
	propview5yr['propertyvalue3y'] = round(float(propview5yr['propertyvalue2y']) + (float(propview5yr['propertyvalue2y']) * float(appraise_rate)))
	propview5yr['propertyvalue4y'] = round(float(propview5yr['propertyvalue3y']) + (float(propview5yr['propertyvalue3y']) * float(appraise_rate)))
	propview5yr['propertyvalue'] = round(float(propview5yr['propertyvalue4y']) + (float(propview5yr['propertyvalue4y']) * float(appraise_rate)))

	repair_rate = float(prop.repairrate/100)
	propview5yr['repairfee1y'] = propview1yr['repairfee1y']
	propview5yr['repairfee2y'] = round(propview5yr['expectedrent2y'] * repair_rate)
	propview5yr['repairfee3y'] = round(propview5yr['expectedrent3y'] * repair_rate)
	propview5yr['repairfee4y'] = round(propview5yr['expectedrent4y'] * repair_rate)
	propview5yr['repairfee5y'] = round(propview5yr['expectedrent5y'] * repair_rate)
	propview5yr['repairfee'] = round(propview5yr['repairfee1y'] + propview5yr['repairfee2y'] + propview5yr['repairfee3y'] + \
								propview5yr['repairfee4y'] + propview5yr['repairfee5y'])

	pm_rate = float(prop.pmrate/100)
	propview5yr['pmfee1y'] = propview1yr['pmfee1y']
	propview5yr['pmfee2y'] = round(propview5yr['expectedrent2y'] * pm_rate)
	propview5yr['pmfee3y'] = round(propview5yr['expectedrent3y'] * pm_rate)
	propview5yr['pmfee4y'] = round(propview5yr['expectedrent4y'] * pm_rate)
	propview5yr['pmfee5y'] = round(propview5yr['expectedrent5y'] * pm_rate)
	propview5yr['pmfee'] = round(propview5yr['pmfee1y'] + propview5yr['pmfee2y'] + propview5yr['pmfee3y'] + \
								propview5yr['pmfee4y'] + propview5yr['pmfee5y'])

	lease_rate = float(prop.leaserate/100)
	propview5yr['leasefee1y'] = propview1yr['leasefee1y']
	propview5yr['leasefee2y'] = round(propview5yr['expectedrent2y'] * lease_rate)
	propview5yr['leasefee3y'] = round(propview5yr['expectedrent3y'] * lease_rate)
	propview5yr['leasefee4y'] = round(propview5yr['expectedrent4y'] * lease_rate)
	propview5yr['leasefee5y'] = round(propview5yr['expectedrent5y'] * lease_rate)
	propview5yr['leasefee'] = round(propview5yr['leasefee1y'] + propview5yr['leasefee2y'] + propview5yr['leasefee3y'] + \
								propview5yr['leasefee4y'] + propview5yr['leasefee5y'])

	try:
		propview5yr['hoafee'] = round(float(propview1yr['hoafee1y'] * 5))
	except:
		propview5yr['hoafee'] = 0.0

	insurance_rate = float(0.02) # Add a static 2% increase per year on insurance
	propview5yr['insurancefee1y'] = propview1yr['insurancefee1y']
	propview5yr['insurancefee2y'] = round((propview5yr['insurancefee1y'] * insurance_rate) + propview5yr['insurancefee1y'])
	propview5yr['insurancefee3y'] = round((propview5yr['insurancefee2y'] * insurance_rate) + propview5yr['insurancefee2y'])
	propview5yr['insurancefee4y'] = round((propview5yr['insurancefee3y'] * insurance_rate) + propview5yr['insurancefee3y'])
	propview5yr['insurancefee5y'] = round((propview5yr['insurancefee4y'] * insurance_rate) + propview5yr['insurancefee4y'])
	propview5yr['insurancefee'] = round(propview5yr['insurancefee1y'] + propview5yr['insurancefee2y'] + propview5yr['insurancefee3y'] + \
								propview5yr['insurancefee4y'] + propview5yr['insurancefee5y'])

	propview5yr['otherfee'] = float(propview1yr['otherfee1y'] * 5)

	propview5yr['nonrepairfee'] = float(propview5yr['insurancefee'] + propview5yr['hoafee'] + propview5yr['leasefee'] + \
								propview5yr['pmfee'] + propview5yr['otherfee'])

	propview5yr['opex'] = float(propview5yr['nonrepairfee'] + propview5yr['repairfee'])

	propview5yr['noi'] = float(propview5yr['expectedrent'] - propview5yr['opex'])

	capex_rate = float(prop.capexrate/100)
	propview5yr['capex1y'] = propview1yr['capex1y']
	propview5yr['capex2y'] = round(propview5yr['expectedrent2y'] * capex_rate)
	propview5yr['capex3y'] = round(propview5yr['expectedrent3y'] * capex_rate)
	propview5yr['capex4y'] = round(propview5yr['expectedrent4y'] * capex_rate)
	propview5yr['capex5y'] = round(propview5yr['expectedrent5y'] * capex_rate)
	propview5yr['capex'] = round(propview5yr['capex1y'] + propview5yr['capex2y'] + propview5yr['capex3y'] + \
								propview5yr['capex4y'] + propview5yr['capex5y'])

	propview5yr['unlevcf'] = float(propview5yr['noi'] - propview5yr['capex'])

	
	# need to add mortgage calculation
	propview5yr['mortgage'] = float(propview1yr['mortgage1y'] * 5)
	propview5yr['principal'] = CalcPrinciple(float(((prop.interestrate)/100)/12), 60, propview1yr['mortgage1m'], propview1yr['original_principle'])
	propview5yr['equity'] = propview5yr['propertyvalue'] - propview5yr['principal']

	propview5yr['totalnetcf'] = float(propview5yr['unlevcf'] - propview5yr['mortgage'])

	propview5yr['posttaxncf'] = round(propview5yr['totalnetcf'] - (propview5yr['totalnetcf'] * StateTaxRate(prop.state)))

	propview5yr['posttaxncfplusequity'] = propview5yr['posttaxncf'] + propview5yr['equity']

	return propview5yr


def PropViewCalc10yr(prop, propview1yr, propview5yr):
	propview10yr = {}
	rent_growth = float(prop.rent_growth / 100)
	propview10yr['expectedrent6y'] = round((propview5yr['expectedrent5y'] * rent_growth) + propview5yr['expectedrent5y'])
	propview10yr['expectedrent7y'] = round((propview10yr['expectedrent6y'] * rent_growth) + propview10yr['expectedrent6y'])
	propview10yr['expectedrent8y'] = round((propview10yr['expectedrent7y'] * rent_growth) + propview10yr['expectedrent7y'])
	propview10yr['expectedrent9y'] = round((propview10yr['expectedrent8y'] * rent_growth) + propview10yr['expectedrent8y'])
	propview10yr['expectedrent10y'] = round((propview10yr['expectedrent9y'] * rent_growth) + propview10yr['expectedrent9y'])
	propview10yr['expectedrent'] = round(propview5yr['expectedrent'] + propview10yr['expectedrent6y'] + propview10yr['expectedrent7y'] + propview10yr['expectedrent8y'] + \
								propview10yr['expectedrent9y'] + propview10yr['expectedrent10y'])

	tax_growth = float(float(prop.tax_rate) / 100)
	propview10yr['propertytaxes6y'] = round((propview5yr['propertytaxes5y'] * tax_growth) + propview5yr['propertytaxes5y'])
	propview10yr['propertytaxes7y'] = round((propview10yr['propertytaxes6y'] * tax_growth) + propview10yr['propertytaxes6y'])
	propview10yr['propertytaxes8y'] = round((propview10yr['propertytaxes7y'] * tax_growth) + propview10yr['propertytaxes7y'])
	propview10yr['propertytaxes9y'] = round((propview10yr['propertytaxes8y'] * tax_growth) + propview10yr['propertytaxes8y'])
	propview10yr['propertytaxes10y'] = round((propview10yr['propertytaxes9y'] * tax_growth) + propview10yr['propertytaxes9y'])
	propview10yr['propertytaxes'] = round(propview5yr['propertytaxes'] + propview10yr['propertytaxes6y'] + propview10yr['propertytaxes7y'] + propview10yr['propertytaxes8y'] + \
								propview10yr['propertytaxes9y'] + propview10yr['propertytaxes10y'])

	appraise_rate = (float(prop.appraise_rate)/100)
	propview10yr['propertyvalue6y'] = round(float(propview5yr['propertyvalue']) + (float(propview5yr['propertyvalue']) * float(appraise_rate)))
	propview10yr['propertyvalue7y'] = round(float(propview10yr['propertyvalue6y']) + (float(propview10yr['propertyvalue6y']) * float(appraise_rate)))
	propview10yr['propertyvalue8y'] = round(float(propview10yr['propertyvalue7y']) + (float(propview10yr['propertyvalue7y']) * float(appraise_rate)))
	propview10yr['propertyvalue9y'] = round(float(propview10yr['propertyvalue8y']) + (float(propview10yr['propertyvalue8y']) * float(appraise_rate)))
	propview10yr['propertyvalue'] = round(float(propview10yr['propertyvalue9y']) + (float(propview10yr['propertyvalue9y']) * float(appraise_rate)))

	repair_rate = float(prop.repairrate/100)
	propview10yr['repairfee6y'] = round(propview10yr['expectedrent6y'] * repair_rate)
	propview10yr['repairfee7y'] = round(propview10yr['expectedrent7y'] * repair_rate)
	propview10yr['repairfee8y'] = round(propview10yr['expectedrent8y'] * repair_rate)
	propview10yr['repairfee9y'] = round(propview10yr['expectedrent9y'] * repair_rate)
	propview10yr['repairfee10y'] = round(propview10yr['expectedrent10y'] * repair_rate)
	propview10yr['repairfee'] = round(propview5yr['repairfee'] + propview10yr['repairfee6y'] + propview10yr['repairfee7y'] + propview10yr['repairfee8y'] + \
								propview10yr['repairfee9y'] + propview10yr['repairfee10y'])

	pm_rate = float(prop.pmrate/100)
	propview10yr['pmfee6y'] = round(propview10yr['expectedrent6y'] * pm_rate)
	propview10yr['pmfee7y'] = round(propview10yr['expectedrent7y'] * pm_rate)
	propview10yr['pmfee8y'] = round(propview10yr['expectedrent8y'] * pm_rate)
	propview10yr['pmfee9y'] = round(propview10yr['expectedrent9y'] * pm_rate)
	propview10yr['pmfee10y'] = round(propview10yr['expectedrent10y'] * pm_rate)
	propview10yr['pmfee'] = round(propview5yr['pmfee'] + propview10yr['pmfee7y'] + propview10yr['pmfee8y'] + \
								propview10yr['pmfee9y'] + propview10yr['pmfee10y'])

	lease_rate = float(prop.leaserate/100)
	propview10yr['leasefee6y'] = round(propview10yr['expectedrent6y'] * lease_rate)
	propview10yr['leasefee7y'] = round(propview10yr['expectedrent7y'] * lease_rate)
	propview10yr['leasefee8y'] = round(propview10yr['expectedrent8y'] * lease_rate)
	propview10yr['leasefee9y'] = round(propview10yr['expectedrent9y'] * lease_rate)
	propview10yr['leasefee10y'] = round(propview10yr['expectedrent10y'] * lease_rate)
	propview10yr['leasefee'] = round(propview5yr['leasefee'] + propview10yr['leasefee6y'] + propview10yr['leasefee7y'] + propview10yr['leasefee8y'] + \
								propview10yr['leasefee9y'] + propview10yr['leasefee10y'])

	try:
		propview10yr['hoafee'] = round(float(propview5yr['hoafee'] * 2))
	except:
		propview10yr['hoafee'] = 0.0

	insurance_rate = float(0.02) # Add a static 2% increase per year on insurance
	propview10yr['insurancefee6y'] = round((propview5yr['insurancefee5y'] * insurance_rate) + propview5yr['insurancefee5y'])
	propview10yr['insurancefee7y'] = round((propview10yr['insurancefee6y'] * insurance_rate) + propview10yr['insurancefee6y'])
	propview10yr['insurancefee8y'] = round((propview10yr['insurancefee7y'] * insurance_rate) + propview10yr['insurancefee7y'])
	propview10yr['insurancefee9y'] = round((propview10yr['insurancefee8y'] * insurance_rate) + propview10yr['insurancefee8y'])
	propview10yr['insurancefee10y'] = round((propview10yr['insurancefee9y'] * insurance_rate) + propview10yr['insurancefee9y'])
	propview10yr['insurancefee'] = round(propview5yr['insurancefee'] + propview10yr['insurancefee6y'] + propview10yr['insurancefee7y'] + propview10yr['insurancefee8y'] + \
								propview10yr['insurancefee9y'] + propview10yr['insurancefee10y'])

	propview10yr['otherfee'] = float(propview1yr['otherfee1y'] * 10)

	propview10yr['nonrepairfee'] = float(propview5yr['nonrepairfee'] + propview10yr['insurancefee'] + propview10yr['hoafee'] + propview10yr['leasefee'] + \
								propview10yr['pmfee'] + propview10yr['otherfee'])

	propview10yr['opex'] = float(propview5yr['opex'] + propview10yr['nonrepairfee'] + propview10yr['repairfee'])

	propview10yr['noi'] = float(propview5yr['noi'] + (propview10yr['expectedrent'] - propview10yr['opex']))

	capex_rate = float(prop.capexrate/100)
	propview10yr['capex6y'] = round(propview10yr['expectedrent6y'] * capex_rate)
	propview10yr['capex7y'] = round(propview10yr['expectedrent7y'] * capex_rate)
	propview10yr['capex8y'] = round(propview10yr['expectedrent8y'] * capex_rate)
	propview10yr['capex9y'] = round(propview10yr['expectedrent9y'] * capex_rate)
	propview10yr['capex10y'] = round(propview10yr['expectedrent10y'] * capex_rate)
	propview10yr['capex'] = round(propview5yr['capex'] + propview10yr['capex6y'] + propview10yr['capex7y'] + propview10yr['capex8y'] + \
								propview10yr['capex9y'] + propview10yr['capex10y'])

	propview10yr['unlevcf'] = float(propview5yr['unlevcf'] + (propview10yr['noi'] - propview10yr['capex']))

	# need to add mortgage calculation
	propview10yr['mortgage'] = float(propview1yr['mortgage1y'] * 10)
	propview10yr['principal'] = CalcPrinciple(float(((prop.interestrate)/100)/12), 120, propview1yr['mortgage1m'], propview1yr['original_principle'])
	propview10yr['equity'] = propview10yr['propertyvalue'] - propview10yr['principal']

	propview10yr['totalnetcf'] = float(propview5yr['totalnetcf'] + (propview10yr['unlevcf'] - propview10yr['mortgage']))

	propview10yr['posttaxncf'] = round(propview10yr['totalnetcf'] - (propview10yr['totalnetcf'] * StateTaxRate(prop.state)))

	propview10yr['posttaxncfplusequity'] = propview10yr['posttaxncf'] + propview10yr['equity']

	return propview10yr


def PropViewCalc15yr(prop, propview1yr, propview5yr, propview10yr):
	propview15yr = {}
	rent_growth = float(prop.rent_growth / 100)
	propview15yr['expectedrent11y'] = round((propview10yr['expectedrent10y'] * rent_growth) + propview10yr['expectedrent10y'])
	propview15yr['expectedrent12y'] = round((propview15yr['expectedrent11y'] * rent_growth) + propview15yr['expectedrent11y'])
	propview15yr['expectedrent13y'] = round((propview15yr['expectedrent12y'] * rent_growth) + propview15yr['expectedrent12y'])
	propview15yr['expectedrent14y'] = round((propview15yr['expectedrent13y'] * rent_growth) + propview15yr['expectedrent13y'])
	propview15yr['expectedrent15y'] = round((propview15yr['expectedrent14y'] * rent_growth) + propview15yr['expectedrent14y'])
	propview15yr['expectedrent'] = round(propview10yr['expectedrent'] + propview15yr['expectedrent11y'] + propview15yr['expectedrent12y'] + propview15yr['expectedrent13y'] + \
								propview15yr['expectedrent14y'] + propview15yr['expectedrent15y'])

	tax_growth = float(float(prop.tax_rate) / 100)
	propview15yr['propertytaxes11y'] = round((propview10yr['propertytaxes10y'] * tax_growth) + propview10yr['propertytaxes10y'])
	propview15yr['propertytaxes12y'] = round((propview15yr['propertytaxes11y'] * tax_growth) + propview15yr['propertytaxes11y'])
	propview15yr['propertytaxes13y'] = round((propview15yr['propertytaxes12y'] * tax_growth) + propview15yr['propertytaxes12y'])
	propview15yr['propertytaxes14y'] = round((propview15yr['propertytaxes13y'] * tax_growth) + propview15yr['propertytaxes13y'])
	propview15yr['propertytaxes15y'] = round((propview15yr['propertytaxes14y'] * tax_growth) + propview15yr['propertytaxes14y'])
	propview15yr['propertytaxes'] = round(propview10yr['propertytaxes'] + propview15yr['propertytaxes11y'] + propview15yr['propertytaxes12y'] + propview15yr['propertytaxes13y'] + \
								propview15yr['propertytaxes14y'] + propview15yr['propertytaxes15y'])

	appraise_rate = (float(prop.appraise_rate)/100)
	propview15yr['propertyvalue11y'] = round(float(propview10yr['propertyvalue']) + (float(propview10yr['propertyvalue']) * float(appraise_rate)))
	propview15yr['propertyvalue12y'] = round(float(propview15yr['propertyvalue11y']) + (float(propview15yr['propertyvalue11y']) * float(appraise_rate)))
	propview15yr['propertyvalue13y'] = round(float(propview15yr['propertyvalue12y']) + (float(propview15yr['propertyvalue12y']) * float(appraise_rate)))
	propview15yr['propertyvalue14y'] = round(float(propview15yr['propertyvalue13y']) + (float(propview15yr['propertyvalue13y']) * float(appraise_rate)))
	propview15yr['propertyvalue'] = round(float(propview15yr['propertyvalue14y']) + (float(propview15yr['propertyvalue14y']) * float(appraise_rate)))

	repair_rate = float(prop.repairrate/100)
	propview15yr['repairfee11y'] = round(propview15yr['expectedrent11y'] * repair_rate)
	propview15yr['repairfee12y'] = round(propview15yr['expectedrent12y'] * repair_rate)
	propview15yr['repairfee13y'] = round(propview15yr['expectedrent13y'] * repair_rate)
	propview15yr['repairfee14y'] = round(propview15yr['expectedrent14y'] * repair_rate)
	propview15yr['repairfee15y'] = round(propview15yr['expectedrent15y'] * repair_rate)
	propview15yr['repairfee'] = round(propview10yr['repairfee'] + propview15yr['repairfee11y'] + propview15yr['repairfee12y'] + propview15yr['repairfee13y'] + \
								propview15yr['repairfee14y'] + propview15yr['repairfee15y'])

	pm_rate = float(prop.pmrate/100)
	propview15yr['pmfee11y'] = round(propview15yr['expectedrent11y'] * pm_rate)
	propview15yr['pmfee12y'] = round(propview15yr['expectedrent12y'] * pm_rate)
	propview15yr['pmfee13y'] = round(propview15yr['expectedrent13y'] * pm_rate)
	propview15yr['pmfee14y'] = round(propview15yr['expectedrent14y'] * pm_rate)
	propview15yr['pmfee15y'] = round(propview15yr['expectedrent15y'] * pm_rate)
	propview15yr['pmfee'] = round(propview10yr['pmfee'] + propview15yr['pmfee11y'] + propview15yr['pmfee12y'] + propview15yr['pmfee13y'] + \
								propview15yr['pmfee14y'] + propview15yr['pmfee15y'])

	lease_rate = float(prop.leaserate/100)
	propview15yr['leasefee11y'] = round(propview15yr['expectedrent11y'] * lease_rate)
	propview15yr['leasefee12y'] = round(propview15yr['expectedrent12y'] * lease_rate)
	propview15yr['leasefee13y'] = round(propview15yr['expectedrent13y'] * lease_rate)
	propview15yr['leasefee14y'] = round(propview15yr['expectedrent14y'] * lease_rate)
	propview15yr['leasefee15y'] = round(propview15yr['expectedrent15y'] * lease_rate)
	propview15yr['leasefee'] = round(propview10yr['leasefee']  + propview15yr['leasefee11y'] + propview15yr['leasefee12y'] + propview15yr['leasefee13y'] + \
								propview15yr['leasefee14y'] + propview15yr['leasefee15y'])

	try:
		propview15yr['hoafee'] = round(float(propview5yr['hoafee'] * 3))
	except:
		propview15yr['hoafee'] = 0.0

	insurance_rate = float(0.02) # Add a static 2% increase per year on insurance
	propview15yr['insurancefee11y'] = round((propview10yr['insurancefee10y'] * insurance_rate) + propview10yr['insurancefee10y'])
	propview15yr['insurancefee12y'] = round((propview15yr['insurancefee11y'] * insurance_rate) + propview15yr['insurancefee11y'])
	propview15yr['insurancefee13y'] = round((propview15yr['insurancefee12y'] * insurance_rate) + propview15yr['insurancefee12y'])
	propview15yr['insurancefee14y'] = round((propview15yr['insurancefee13y'] * insurance_rate) + propview15yr['insurancefee13y'])
	propview15yr['insurancefee15y'] = round((propview15yr['insurancefee14y'] * insurance_rate) + propview15yr['insurancefee14y'])
	propview15yr['insurancefee'] = round(propview10yr['insurancefee'] + propview15yr['insurancefee11y'] + propview15yr['insurancefee12y'] + propview15yr['insurancefee13y'] + \
								propview15yr['insurancefee14y'] + propview15yr['insurancefee15y'])

	propview15yr['otherfee'] = float(propview1yr['otherfee1y'] * 15)

	propview15yr['nonrepairfee'] = float(propview10yr['nonrepairfee'] + propview15yr['insurancefee'] + propview15yr['hoafee'] + propview15yr['leasefee'] + \
								propview15yr['pmfee'] + propview15yr['otherfee'])

	propview15yr['opex'] = float(propview10yr['opex'] + propview15yr['nonrepairfee'] + propview15yr['repairfee'])

	propview15yr['noi'] = float(propview10yr['noi']  + (propview15yr['expectedrent'] - propview15yr['opex']))

	capex_rate = float(prop.capexrate/100)
	propview15yr['capex11y'] = round(propview15yr['expectedrent11y'] * capex_rate)
	propview15yr['capex12y'] = round(propview15yr['expectedrent12y'] * capex_rate)
	propview15yr['capex13y'] = round(propview15yr['expectedrent13y'] * capex_rate)
	propview15yr['capex14y'] = round(propview15yr['expectedrent14y'] * capex_rate)
	propview15yr['capex15y'] = round(propview15yr['expectedrent15y'] * capex_rate)
	propview15yr['capex'] = round(propview10yr['capex'] + propview15yr['capex11y'] + propview15yr['capex12y'] + propview15yr['capex13y'] + \
								propview15yr['capex14y'] + propview15yr['capex15y'])

	propview15yr['unlevcf'] = float(propview10yr['unlevcf'] + (propview15yr['noi'] - propview15yr['capex']))

	
	propview15yr['mortgage'] = float(propview1yr['mortgage1y'] * 15)
	propview15yr['principal'] = CalcPrinciple(float(((prop.interestrate)/100)/12), 180, propview1yr['mortgage1m'], propview1yr['original_principle'])
	propview15yr['equity'] = propview15yr['propertyvalue'] - propview15yr['principal']

	propview15yr['totalnetcf'] = float(propview10yr['totalnetcf'] + (propview15yr['unlevcf'] - propview15yr['mortgage']))

	propview15yr['posttaxncf'] = round(propview15yr['totalnetcf'] - (propview15yr['totalnetcf'] * StateTaxRate(prop.state)))

	propview15yr['posttaxncfplusequity'] = propview15yr['posttaxncf'] + propview15yr['equity']

	return propview15yr


### API Call Functions

def RunFreeAPI(prop):
	### Zillow API Fetch
	try:
		# Call ZillowAPI models
		zillowapi = ApiStore.objects.get(name='Zillow GetDeepSearch')

		params = { "address": prop.address, "citystatezip": prop.zipcode, "rentzestimate" : 'True', "zws-id": zillowapi.key }
		headers = { "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" }
	
		zillow_dict = {}

		attribute_mapping = {
		"bathrooms": "result/bathrooms",
		"bedrooms": "result/bedrooms",
		"city": "result/address/city",
		"fips_county": "result/FIPScounty",
		"homesize": "result/finishedSqFt",
		"last_sold_date": "result/lastSoldDate",
		"last_sold_price": "result/lastSoldPrice",
		"latitude": "result/address/latitude",
		"longitude": "result/address/longitude",
		"lotsize": "result/lotSizeSqFt",
		"rentzestimate": "result/rentzestimate/amount",
		"rentzestimate_last_updated": "result/rentzestimate/last-updated",
		"rentzestimate_high": "result/rentzestimate/valuationRange/high",
		"rentzestimate_low": "result/rentzestimate/valuationRange/low",
		"state": "result/address/state",
		"address": "result/address/street",
		"taxvalue": "result/taxAssessment",
		"taxyear": "result/taxAssessmentYear",
		"use_code": "result/useCode",
		"yearbuilt": "result/yearBuilt",
		"zestimate": "result/zestimate/amount",
		"zestimate_last_updated": "result/zestimate/last-updated",
		"zestimate_high": "result/zestimate/valuationRange/high",
		"zestimate_low": "result/zestimate/valuationRange/low",
		"zillow_id": "result/zpid",
		"zillow_link": "result/links/mapthishome",
		"zipcode": "result/address/zipcode",
		}

		try:
			request = requests.get(url=zillowapi.url, params=params, headers=headers)
		except (
 		requests.exceptions.ConnectionError,
 		requests.exceptions.TooManyRedirects,
 		requests.exceptions.Timeout,
 		):
 			pass
 
		try:
 			response = ElementTree.fromstring(request.text)
		except ElementTree.ParseError:
 			pass

		if response.findall("message/code")[0].text != 0:
 			pass

		data = response.findall("response/results")[0]
		
		for attr in attribute_mapping:
 			try:
  				value = data.find(attribute_mapping[attr]).text
  				zillow_dict[attr] = value
 			except:
  				pass

		for key in zillow_dict:
 			if hasattr(prop, key):
  				setattr(prop, key, zillow_dict[key])
		
		#prop.save()
  
	except ObjectDoesNotExist:
 	# This is the try zillowapi loop exception
 	# Populating model will be in try portion so nothing will happen to model/update
 		pass

	### Bridge API Public Assessments
	try:
		# Call BridgeAPI-Pub models
		bridgeapi_pub = ApiStore.objects.get(name='Bridge Public Assessment')
 		
		today = str(datetime.date.today())
		curr_year = int(today[:4])

		taxAmountdict = {curr_year-1: '', curr_year-2: '', curr_year-3: '', curr_year-4: '', curr_year-5: ''} 
		appraisalAmountdict = {curr_year-1: '', curr_year-2: '', curr_year-3: '', curr_year-4: '', curr_year-5: ''}

		params = {"address.full": prop.addressfull, "sortBy": 'year'}
		headers = {"Authorization": "Bearer " + bridgeapi_pub.key, "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

		try:
			response = requests.request('GET', bridgeapi_pub.url, headers=headers, params=params)
		except (
		requests.exceptions.ConnectionError,
		requests.exceptions.TooManyRedirects,
		requests.exceptions.Timeout,
		):
			pass

		for yr in response.json()['bundle']:
			for key in taxAmountdict:
				if yr['taxYear'] == key:
					taxAmountdict[yr['taxYear']] = yr['taxAmount']

		for yr in response.json()['bundle']:
			for key in appraisalAmountdict:
				if yr['year'] == key:
					appraisalAmountdict[yr['year']] = yr['totalValue']

		# Replace 0 values with last year's value
		for attr in taxAmountdict:
			if taxAmountdict[attr] == '' or taxAmountdict[attr] is None:
				try:
					taxAmountdict[attr] = taxAmountdict[attr-1]
				except KeyError:
					try:
						taxAmountdict[attr] = taxAmountdict[attr+1]
					except KeyError:
						taxAmountdict[attr] = '0'
			else:
				taxAmountdict[attr] = taxAmountdict[attr]

		# Replace 0 values with last year's value
		for attr in appraisalAmountdict:
			if appraisalAmountdict[attr] == '':
				try:
					appraisalAmountdict[attr] = appraisalAmountdict[attr-1]
				except KeyError:
					try:
						appraisalAmountdict[attr] = appraisalAmountdict[attr+1]
					except KeyError:
						appraisalAmountdict[attr] = '0'
			else:
				appraisalAmountdict[attr] = appraisalAmountdict[attr]
	
		# Determine Appraise rate over year
		taxList = []
		taxSum = 0.0
		for attr in taxAmountdict:
			try:
				taxList.append(float(taxAmountdict[attr]))
			except:
				taxList.append(float(1))
		for a, b in zip(taxList[::1], taxList[1::1]):
			taxSum = taxSum + float(100 * (a - b) / b)
		taxAvgYoY = taxSum / (len(taxList) - 1)

		# Determine Appraise rate over year
		appraisalList = []
		appraisalSum = 0.0
		for attr in appraisalAmountdict:
			try:
				appraisalList.append(float(appraisalAmountdict[attr]))
			except:
				appraisalList.append(float(1))
		for a, b in zip(appraisalList[::1], appraisalList[1::1]):
			appraisalSum = appraisalSum + float(100 * (a - b) / b)
		appraisalAvgYoY = appraisalSum / (len(appraisalList) - 1)

		# Update the Model Years
		prop.yr1 = curr_year-1
		prop.yr2 = curr_year-2
		prop.yr3 = curr_year-3
		prop.yr4 = curr_year-4
		prop.yr5 = curr_year-5
 		# Add the Appraisals and Tax Amounts to Model
 		# We can do this in order since we filtered the request by year
		prop.tax_yr1 = taxAmountdict[curr_year-1]
		prop.tax_yr2 = taxAmountdict[curr_year-2]
		prop.tax_yr3 = taxAmountdict[curr_year-3]
		prop.tax_yr4 = taxAmountdict[curr_year-4]
		prop.tax_yr5 = taxAmountdict[curr_year-5]
		prop.appraise_yr1 = appraisalAmountdict[curr_year-1]
		prop.appraise_yr2 = appraisalAmountdict[curr_year-2]
		prop.appraise_yr3 = appraisalAmountdict[curr_year-3]
		prop.appraise_yr4 = appraisalAmountdict[curr_year-4]
		prop.appraise_yr5 = appraisalAmountdict[curr_year-5]
		prop.tax_rate = str(taxAvgYoY)
		prop.appraise_rate = str(appraisalAvgYoY)
		# Don't forget the County
		prop.county = response.json()['bundle'][0]['county']
		# And Owner information + occupancy status
		prop.owner_name = response.json()['bundle'][0]['ownerName'][0]
		try:
			if response.json()['bundle'][0]['building'][0]['occupancyStatus']:
				prop.occupancy_status = response.json()['bundle'][0]['building'][0]['occupancyStatus']
		except:
			prop.occupancy_status = 'N/A'
 		# Save the Model
		#prop.save()

	except ObjectDoesNotExist:
 	# This is the try BridgeAPI-Pub loop exception
 	# Populating model will be in try portion so nothing will happen to model/update
		pass

	### Area Vibes
	areavibes_location = prop.address
	areavibes_url1 = 'http://www.areavibes.com/{}-{}/livability/'.format(
		prop.city,
		prop.state)
	areavibes_url2 = '?addr={}&ll={}+{}'.format(
		areavibes_location.replace(" ", "+"),
		prop.latitude, prop.longitude)
	areavibes_url = areavibes_url1 + areavibes_url2
	r = requests.get(areavibes_url)
	soup = BeautifulSoup(r.content, 'html.parser')
	info_block = soup.find_all('nav', class_='category-menu-new')
	try:
		result_string = info_block[0].get_text()
	except IndexError:
		result_string = 'Unknown'

	parsed = ''
	livability = 0
	cost_of_living = ''
	crime = ''
	employment = ''
	housing = ''
	schools = ''
	user_ratings = ''

	try:
		parsed = re.search('Livability(.*?)Amenities(.*?)Cost of Living(.*?)Crime(.*?)Employment(.*?)Housing(.*?)Schools(.*?)User Ratings(.*?)$', result_string)
	except AttributeError:
		livability = 0
		cost_of_living = ''
		crime = ''
		employment = ''
		housing = ''
		schools = ''
		user_ratings = ''
	if parsed:
		try:
			livability = int(parsed.group(1))
		except IndexError:
			livability = 0
		try:
			cost_of_living = parsed.group(3)
		except IndexError:
			cost_of_living = ''
		try:
			crime = parsed.group(4)
		except IndexError:
			crime = ''
		try:
			employment = parsed.group(5)
		except IndexError:
			employment = ''
		try:
			housing = parsed.group(6)
		except IndexError:
			housing = ''
		try:
			schools = parsed.group(7)
		except IndexError:
			schools = ''
		try:
			user_ratings = parsed.group(8)
		except IndexError:
			user_ratings = ''

	prop.av_livability = livability
	prop.av_crime = crime
	prop.av_cost_of_living = cost_of_living
	prop.av_schools = schools
	prop.av_employment = employment
	prop.av_housing = housing
	prop.av_user_ratings = user_ratings

	### FEMA Records
	last_five_years = [str(curr_year-i) for i in range(5)]

	local_disasters = []
	femaurls = []
	disaster_dict = {}
	if 'County' in prop.county:
		county_pattern = re.search('^(.*?) County', prop.county)
		try:
			county = county_pattern.group(1)
		except AttributeError:
			county = prop.county
	else:
		county = prop.county
	for year in last_five_years:
		url1 = 'https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?'
		url2 = "$filter=substringof('{}',designatedArea) and state eq '{}' and fyDeclared eq '{}'".format(
			county, prop.state.upper(), year)
		femaurl1 = url1+url2
		femaurls.append(femaurl1)
	for femaurl in femaurls:
		resp = requests.get(femaurl)
		resp_json = resp.json()
		try:
			random_pick_disaster = random.choice(resp_json['DisasterDeclarationsSummaries'])
			local_disasters.append(random_pick_disaster)
		except IndexError:
			continue

	disaster_list = []
	z = 1
	
	if local_disasters:
		for disaster in local_disasters:
			disaster_list.append(str(disaster['fyDeclared']) + ' - ' + str(disaster['designatedArea']) + ' - ' + str(disaster['declarationTitle']))

	
	for report in disaster_list:
			attrkey = 'fema' + str(z)
			setattr(prop, attrkey, report)
			z = z + 1

	#prop.save()

	### Great Schools API Fetch
	try:
		# Call Greatschools models
		gsapi = ApiStore.objects.get(name='Great Schools')
		try:
			gsheaders = {'x-api-key': gsapi.key}
			# Search Elementary Schools
			gsparams_e = {'lat': prop.latitude, 'lon': prop.longitude, \
			'school_type': 'public', 'level_codes': 'e', 'limit': '1', \
			'distance': '5'}
			gsparams_m = {'lat': prop.latitude, 'lon': prop.longitude, \
			'school_type': 'public', 'level_codes': 'm', 'limit': '1', \
			'distance': '5'}
			gsparams_h = {'lat': prop.latitude, 'lon': prop.longitude, \
			'school_type': 'public', 'level_codes': 'h', 'limit': '1', \
			'distance': '5'}

			gsresponse_e = requests.request('GET', gsapi.url, headers=gsheaders, params=gsparams_e)
			gsresponse_m = requests.request('GET', gsapi.url, headers=gsheaders, params=gsparams_m)
			gsresponse_h = requests.request('GET', gsapi.url, headers=gsheaders, params=gsparams_h)

			gs_name_e = gsresponse_e.json()['schools'][0]['name']
			gs_rating_e = str(gsresponse_e.json()['schools'][0]['rating'])
			gs_name_m = gsresponse_m.json()['schools'][0]['name']
			gs_rating_m = str(gsresponse_m.json()['schools'][0]['rating'])
			gs_name_h = gsresponse_h.json()['schools'][0]['name']
			gs_rating_h = str(gsresponse_h.json()['schools'][0]['rating'])

			prop.gs_name_e = gs_name_e
			prop.gs_name_m = gs_name_m
			prop.gs_name_h = gs_name_h
			prop.gs_rating_e = gs_rating_e
			prop.gs_rating_m = gs_rating_m
			prop.gs_rating_h = gs_rating_h
			#prop.save()

		except (
		requests.exceptions.ConnectionError,
		requests.exceptions.TooManyRedirects,
		requests.exceptions.Timeout,
		):
			pass

	except ObjectDoesNotExist:
 	# This is the try gsapi loop exception
 	# Populating model will be in try portion so nothing will happen to model/update
		pass


	### Google Maps API Fetch
	try:
		# Call GoogleAPI models
 		googleapi = ApiStore.objects.get(name='Google Maps')
 		if prop.image_url:
 			pass
 		else:
 			size = '600x400'
 			street = prop.address
 			street = street.replace(" ", "+")
 			location = street + '+' + prop.city + '+' + prop.state
 			fov = '100'
 			heading = '80'
 			pitch = '0'
 
	 		url = googleapi.url + '?size=' + size + '&location=' + location + '&fov=' + fov + '&heading=' + heading + '&pitch=' + pitch + '&key=' + googleapi.key
 
	 		prop.image_url = url
 
 			#prop.save()
 
	except ObjectDoesNotExist:
 	# This is the try googleapi loop exception
 	# Populating model will be in try portion so nothing will happen to model/update
 		pass

 	### US Census Bureau's 1-year ACS for 2019 API Call
	try:
 		# Call Census Bureau API modle
		censusapi = ApiStore.objects.get(name='US Census Bureau 2019')
 		# Expecting base URL similar to: https://api.census.gov/data/2019/acs/acs1
		censusurl1 = '?get=NAME,'
		censusurl2 = '&for=place:*&in=state:*'
		censusurl_var1 = 'B25008_003E' # Renter Occupied
		censusurl_var2 = 'B25004_003E' # Rented, Not Occupied
		censusurl_var3 = 'B25004_002E' # For Rent

		census_state = ConvertStateName(prop.state) # Get Full Name

		url_rentocc = censusapi.url + censusurl1 + censusurl_var1 + censusurl2
		url_rentnotocc = censusapi.url + censusurl1 + censusurl_var2 + censusurl2
		url_forrent = censusapi.url + censusurl1 + censusurl_var3 + censusurl2

		resp_rentocc = requests.request('GET', url_rentocc)
		resp_rentnotocc = requests.request('GET', url_rentnotocc)
		resp_forrent = requests.request('GET', url_forrent)

		for place in resp_rentocc.json():
			if re.match(prop.city + '.(city|town|village).\s' + census_state, place[0]):
				rentocc = place[1]

		for place in resp_rentnotocc.json():
			if re.match(prop.city + '.(city|town|village).\s' + census_state, place[0]):
				rentnotocc = place[1]

		for place in resp_forrent.json():
			if re.match(prop.city + '.(city|town|village).\s' + census_state, place[0]):
				forrent = place[1]

		# Census Bureau states vacancy rate is 'For Rent' divided by the sum of 
		# Renter Occupied', 'Rented, Not Occupied', & 'For Rent'.

		newvacancyrate = (float(forrent) / (float(rentocc) + float(rentnotocc) + float(forrent))) * 100
		prop.vacancyrate = round(newvacancyrate, 2)
		#prop.save()

	except:
		# Try scrapping vacancy rates from  infoplease.com if exception
		try:
			infoplease_baseurl = 'https://www.infoplease.com/us/census/'
			infoplease_tailurl = '/demographic-statistics'
			infoplease_state = ConvertStateName(prop.state) # Get Full Name
			infoplease_city1 = prop.city
			infoplease_city = infoplease_city1.replace(" ", "-")
			
			infoplease_url = infoplease_baseurl + infoplease_state + '/' + infoplease_city + infoplease_tailurl

			infoplease_resp = requests.request('GET', infoplease_url)

			infoplease_tree = html.fromstring(infoplease_resp.content)

			newvacancyrate = float(infoplease_tree.xpath('//*[@id="table1"]/tbody/tr[112]/td[2]/text()')[0])
			prop.vacancyrate = round(newvacancyrate, 2)
			#prop.save()

		except:
			pass

	prop.save()

def PropListCalcs(prop):
	# List for rei_properties_view to check empty values
	propertyValuesMassage = ['last_sold_price', 'zestimate', 'rentzestimate']

	# Run through the calculations first before we muck around with values...
	# Below will calculate rates like down payment, closing costs, etc...
	prop.zestimate = '0' if prop.zestimate == '' else prop.zestimate
	prop.rentzestimate = '0' if prop.rentzestimate == '' else prop.rentzestimate
	prop.sales_price = prop.zestimate if prop.sales_price == '' else prop.sales_price
	prop.rent_price = prop.rentzestimate if prop.rent_price == '' else prop.rent_price
	# CRUNCH THE NUMBERS
	propview1yr = PropViewCalc1yr(prop)

	# Massage Proforma Summary Data
	try:
		# Calc Proforma Data
		propview1yr['caprate'] = propview1yr['noi1y'] / float(prop.sales_price)
		propview1yr['cashoncash'] = propview1yr['totalnetcf1y'] / (float(DownPayment(prop.sales_price, prop.downpayment)) + float(ClosingCosts(prop.sales_price, prop.state)))
		propview1yr['onepercentrule'] = float(prop.rent_price) / float(prop.sales_price)
		propview1yr['totalinvestment'] = DownPayment(prop.sales_price, prop.downpayment) + ClosingCosts(prop.sales_price, prop.state)
		propview1yr['annreturn'] = (float(propview1yr['cashoncash']) * 100) +  (propview1yr['totalinvestment'] /  (propview1yr['propertyvalue'] - float(prop.sales_price)))

		# Massage for output
		propview1yr['caprate'] = '{:.2f}%'.format(float((propview1yr['caprate'] * 100)))
		propview1yr['cashoncash'] = '{:.2f}%'.format(float((propview1yr['cashoncash'] * 100)))
		propview1yr['onepercentrule'] = '{:.2f}%'.format(float((propview1yr['onepercentrule'] * 100)))
		propview1yr['totalinvestment'] = '${:,.0f}'.format(float(propview1yr['totalinvestment']))
		propview1yr['annreturn'] = '{:.2f}%'.format(float(propview1yr['annreturn']))
	except ZeroDivisionError:
		propview1yr['caprate'] = '0'
		propview1yr['cashoncash'] = '0'
		propview1yr['onepercentrule'] = '0'
		propview1yr['totalinvestment'] = '0'
		propview1yr['annreturn'] = '0'

	# Massage rest of Proforma Summary Data
	prop.sales_price = '${:,.0f}'.format(float(prop.sales_price))
	prop.rent_price = '${:,.0f}'.format(float(prop.rent_price))

	try:
		# Massage Monthly Cashflow
		propview1yr['expectedrent1m'] = '${:,.0f}'.format(float(propview1yr['expectedrent1m']))
		propview1yr['totalnetcf1y'] = '${:,.0f}'.format(float(propview1yr['totalnetcf1y']))
	except:
		propview1yr['expectedrent1m'] = '0'
		propview1yr['totalnetcf1y'] = '0'

	# Modify prop values to display on template as "$0.00"
	for attr in propertyValuesMassage:
		if hasattr(prop, attr):
			if getattr(prop, attr) == '':
				setattr(prop, attr, '$0')
			else:
				setattr(prop, attr, '${:,.0f}'.format(float(getattr(prop, attr))))
		else:
			pass

	return prop, propview1yr


def PropViewCalcs(prop):
	# List for rei_properties_view to check empty values
	propertyValuesMassage = ['last_sold_price', 'zestimate', 'zestimate_low', 'zestimate_high', \
					'rentzestimate', 'rentzestimate_low', 'rentzestimate_high', 'appraise_yr1', \
					'appraise_yr2', 'appraise_yr3', 'appraise_yr4', 'appraise_yr5', 'tax_yr1', \
					'tax_yr2', 'tax_yr3', 'tax_yr4', 'tax_yr5']

	# Run through the calculations first before we muck around with values...
	# Below will calculate rates like down payment, closing costs, etc...
	prop.zestimate = '0' if prop.zestimate == '' else prop.zestimate
	prop.rentzestimate = '0' if prop.rentzestimate == '' else prop.rentzestimate
	prop.sales_price = prop.zestimate if prop.sales_price == '' else prop.sales_price
	prop.rent_price = prop.rentzestimate if prop.rent_price == '' else prop.rent_price
	# CRUNCH THE NUMBERS
	propview1yr = PropViewCalc1yr(prop)
	propview5yr = PropViewCalc5yr(prop, propview1yr)
	propview10yr = PropViewCalc10yr(prop, propview1yr, propview5yr)
	propview15yr = PropViewCalc15yr(prop, propview1yr, propview5yr, propview10yr)

	# Massage Proforma Summary Data
	try:
		# Calc Proforma Data
		propview1yr['grossyield'] = propview1yr['expectedrent1y'] / float(prop.sales_price)
		propview1yr['caprate'] = propview1yr['noi1y'] / float(prop.sales_price)
		propview1yr['cashoncash'] = propview1yr['totalnetcf1y'] / (float(DownPayment(prop.sales_price, prop.downpayment)) + float(ClosingCosts(prop.sales_price, prop.state)))
		propview1yr['onepercentrule'] = float(prop.rent_price) / float(prop.sales_price)
		propview1yr['totalinvestment'] = DownPayment(prop.sales_price, prop.downpayment) + ClosingCosts(prop.sales_price, prop.state)
		propview1yr['annreturn'] = (float(propview1yr['cashoncash']) * 100) +  (propview1yr['totalinvestment'] /  (propview1yr['propertyvalue'] - float(prop.sales_price)))

		# Massage for output
		propview1yr['grossyield'] = '{:.2f}%'.format(float((propview1yr['grossyield'] * 100)))
		propview1yr['caprate'] = '{:.2f}%'.format(float((propview1yr['caprate'] * 100)))
		propview1yr['cashoncash'] = '{:.2f}%'.format(float((propview1yr['cashoncash'] * 100)))
		propview1yr['onepercentrule'] = '{:.2f}%'.format(float((propview1yr['onepercentrule'] * 100)))
		propview1yr['totalinvestment'] = '${:,.0f}'.format(float(propview1yr['totalinvestment']))
		propview1yr['annreturn'] = '{:.2f}%'.format(float(propview1yr['annreturn']))
	except ZeroDivisionError:
		pass

	# Massage the other Proforma Summary Data
	prop.down = '${:,.0f}'.format(DownPayment(prop.sales_price, prop.downpayment)) # Must be done before sales_price massage
	prop.closingcost = '${:,.0f}'.format(ClosingCosts(prop.sales_price, prop.state)) # Must be done before sales_price massage

	# Massage rest of Proforma Summary Data
	prop.sales_price = '${:,.0f}'.format(float(prop.sales_price))
	prop.rent_price = '${:,.0f}'.format(float(prop.rent_price))
	

	# Massage Public Record Data
	prop.appraise_rate = '{:.2f}%'.format(float(prop.appraise_rate))
	prop.tax_rate = '{:.2f}%'.format(float(prop.tax_rate))

	# Massage Monthly Cashflow
	propview1yr['vacancyfactor'] = '${:,.0f}'.format(float(propview1yr['vacancyfactor']))
	propview1yr['expectedrent1m'] = '${:,.0f}'.format(float(propview1yr['expectedrent1m']))
	propview1yr['expectedrent1y'] = '${:,.0f}'.format(float(propview1yr['expectedrent1y']))
	propview1yr['propertytaxes1m'] = '${:,.0f}'.format(float(propview1yr['propertytaxes1m']))
	propview1yr['propertytaxes1y'] = '${:,.0f}'.format(float(propview1yr['propertytaxes1y']))
	propview1yr['pmfee1m'] = '${:,.0f}'.format(float(propview1yr['pmfee1m']))
	propview1yr['pmfee1y'] = '${:,.0f}'.format(float(propview1yr['pmfee1y']))
	propview1yr['leasefee1m'] = '${:,.0f}'.format(float(propview1yr['leasefee1m']))
	propview1yr['leasefee1y'] = '${:,.0f}'.format(float(propview1yr['leasefee1y']))
	propview1yr['hoafee1m'] = '${:,.0f}'.format(float(propview1yr['hoafee1m']))
	propview1yr['hoafee1y'] = '${:,.0f}'.format(float(propview1yr['hoafee1y']))
	propview1yr['insurancefee1m'] = '${:,.0f}'.format(float(propview1yr['insurancefee1m']))
	propview1yr['insurancefee1y'] = '${:,.0f}'.format(float(propview1yr['insurancefee1y']))
	propview1yr['otherfee1m'] = '${:,.0f}'.format(float(propview1yr['otherfee1m']))
	propview1yr['otherfee1y'] = '${:,.0f}'.format(float(propview1yr['otherfee1y']))
	propview1yr['nonrepairfee1y'] = '${:,.0f}'.format(float(propview1yr['nonrepairfee1y']))
	propview1yr['repairfee1m'] = '${:,.0f}'.format(float(propview1yr['repairfee1m']))
	propview1yr['repairfee1y'] = '${:,.0f}'.format(float(propview1yr['repairfee1y']))
	propview1yr['opex1m'] = '${:,.0f}'.format(float(propview1yr['opex1m']))
	propview1yr['opex1y'] = '${:,.0f}'.format(float(propview1yr['opex1y']))
	propview1yr['noi1m'] = '${:,.0f}'.format(float(propview1yr['noi1m']))
	propview1yr['noi1y'] = '${:,.0f}'.format(float(propview1yr['noi1y']))
	propview1yr['capex1m'] = '${:,.0f}'.format(float(propview1yr['capex1m']))
	propview1yr['capex1y'] = '${:,.0f}'.format(float(propview1yr['capex1y']))
	propview1yr['unlevcf1m'] = '${:,.0f}'.format(float(propview1yr['unlevcf1m']))
	propview1yr['unlevcf1y'] = '${:,.0f}'.format(float(propview1yr['unlevcf1y']))
	propview1yr['mortgage1m'] = '${:,.0f}'.format(float(propview1yr['mortgage1m']))
	propview1yr['mortgage1y'] = '${:,.0f}'.format(float(propview1yr['mortgage1y']))
	propview1yr['totalnetcf1m'] = '${:,.0f}'.format(float(propview1yr['totalnetcf1m']))
	propview1yr['totalnetcf1y'] = '${:,.0f}'.format(float(propview1yr['totalnetcf1y']))
	propview1yr['posttaxncf'] = '${:,.0f}'.format(float(propview1yr['posttaxncf']))
	propview1yr['propertyvalue'] = '${:,.0f}'.format(float(propview1yr['propertyvalue']))
	propview1yr['principal'] = '${:,.0f}'.format(float(propview1yr['principal']))
	propview1yr['equity'] = '${:,.0f}'.format(float(propview1yr['equity']))
	propview1yr['posttaxncfplusequity'] = '${:,.0f}'.format(float(propview1yr['posttaxncfplusequity']))
	# Massage Year 5 Cashflow
	propview5yr['expectedrent'] = '${:,.0f}'.format(float(propview5yr['expectedrent']))
	propview5yr['propertytaxes'] = '${:,.0f}'.format(float(propview5yr['propertytaxes']))
	propview5yr['repairfee'] = '${:,.0f}'.format(float(propview5yr['repairfee']))
	propview5yr['nonrepairfee'] = '${:,.0f}'.format(float(propview5yr['nonrepairfee']))
	propview5yr['noi'] = '${:,.0f}'.format(float(propview5yr['noi']))
	propview5yr['capex'] = '${:,.0f}'.format(float(propview5yr['capex']))
	propview5yr['unlevcf'] = '${:,.0f}'.format(float(propview5yr['unlevcf']))
	propview5yr['mortgage'] = '${:,.0f}'.format(float(propview5yr['mortgage']))
	propview5yr['totalnetcf'] = '${:,.0f}'.format(float(propview5yr['totalnetcf']))
	propview5yr['posttaxncf'] = '${:,.0f}'.format(float(propview5yr['posttaxncf']))
	propview5yr['propertyvalue'] = '${:,.0f}'.format(float(propview5yr['propertyvalue']))
	propview5yr['principal'] = '${:,.0f}'.format(float(propview5yr['principal']))
	propview5yr['equity'] = '${:,.0f}'.format(float(propview5yr['equity']))
	propview5yr['posttaxncfplusequity'] = '${:,.0f}'.format(float(propview5yr['posttaxncfplusequity']))
	# Massage Year 10 Cashflow
	propview10yr['expectedrent'] = '${:,.0f}'.format(float(propview10yr['expectedrent']))
	propview10yr['propertytaxes'] = '${:,.0f}'.format(float(propview10yr['propertytaxes']))
	propview10yr['repairfee'] = '${:,.0f}'.format(float(propview10yr['repairfee']))
	propview10yr['nonrepairfee'] = '${:,.0f}'.format(float(propview10yr['nonrepairfee']))
	propview10yr['noi'] = '${:,.0f}'.format(float(propview10yr['noi']))
	propview10yr['capex'] = '${:,.0f}'.format(float(propview10yr['capex']))
	propview10yr['unlevcf'] = '${:,.0f}'.format(float(propview10yr['unlevcf']))
	propview10yr['mortgage'] = '${:,.0f}'.format(float(propview10yr['mortgage']))
	propview10yr['totalnetcf'] = '${:,.0f}'.format(float(propview10yr['totalnetcf']))
	propview10yr['posttaxncf'] = '${:,.0f}'.format(float(propview10yr['posttaxncf']))
	propview10yr['propertyvalue'] = '${:,.0f}'.format(float(propview10yr['propertyvalue']))
	propview10yr['principal'] = '${:,.0f}'.format(float(propview10yr['principal']))
	propview10yr['equity'] = '${:,.0f}'.format(float(propview10yr['equity']))
	propview10yr['posttaxncfplusequity'] = '${:,.0f}'.format(float(propview10yr['posttaxncfplusequity']))
	# Massage Year 15 Cashflow
	propview15yr['expectedrent'] = '${:,.0f}'.format(float(propview15yr['expectedrent']))
	propview15yr['propertytaxes'] = '${:,.0f}'.format(float(propview15yr['propertytaxes']))
	propview15yr['repairfee'] = '${:,.0f}'.format(float(propview15yr['repairfee']))
	propview15yr['nonrepairfee'] = '${:,.0f}'.format(float(propview15yr['nonrepairfee']))
	propview15yr['noi'] = '${:,.0f}'.format(float(propview15yr['noi']))
	propview15yr['capex'] = '${:,.0f}'.format(float(propview15yr['capex']))
	propview15yr['unlevcf'] = '${:,.0f}'.format(float(propview15yr['unlevcf']))
	propview15yr['mortgage'] = '${:,.0f}'.format(float(propview15yr['mortgage']))
	propview15yr['totalnetcf'] = '${:,.0f}'.format(float(propview15yr['totalnetcf']))
	propview15yr['posttaxncf'] = '${:,.0f}'.format(float(propview15yr['posttaxncf']))
	propview15yr['propertyvalue'] = '${:,.0f}'.format(float(propview15yr['propertyvalue']))
	propview15yr['principal'] = '${:,.0f}'.format(float(propview15yr['principal']))
	propview15yr['equity'] = '${:,.0f}'.format(float(propview15yr['equity']))
	propview15yr['posttaxncfplusequity'] = '${:,.0f}'.format(float(propview15yr['posttaxncfplusequity']))

	# Modify prop values to display on template as "$0.00"
	for attr in propertyValuesMassage:
		if hasattr(prop, attr):
			if getattr(prop, attr) == '':
				setattr(prop, attr, '$0')
			else:
				setattr(prop, attr, '${:,.0f}'.format(float(getattr(prop, attr))))
		else:
			pass

	# Create Google Map
	googleapi = ApiStore.objects.get(name='Google Maps')
	googleapi_key = googleapi.key
	street = prop.address
	street = street.replace(" ", "+")
	location = street + '+' + prop.city + ',' + prop.state

	return prop, location, googleapi_key, propview1yr, propview5yr, propview10yr, propview15yr