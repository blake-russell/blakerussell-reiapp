from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.contrib.auth.models import Permission, User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django_xhtml2pdf.utils import generate_pdf, pdf_decorator
from django import forms
from blakerussell import settings
from blakerussell.models import *
from blakerussell.forms import *
from blakerussell.scripts import *


# Create your views here.

def home(request):
        return render(request, 'blakerussell/home.html', {})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required(login_url='/accounts/login/')
def dashboard(request):
	statusmessages = []
	if not User.objects.all():
		statusmessages.append('- No users exist. Create superuser in shell: "python manage.py createsuperuser"')
	return render(request, 'blakerussell/dashboard.html', {'statusmessages': statusmessages})

@login_required(login_url='/accounts/login/')
def rei_dashboard(request):
	return render(request, 'rei/rei_dashboard.html', {})

@login_required(login_url='/accounts/login/')
def rei_submit(request):
    if request.method == 'POST':
        form = PropertyFormSub(request.POST)
        usersNgroup = Group.objects.get(name="re-admin").user_set.all()
        userName = User.objects.get(username=request.user.username)
        if form.is_valid():
            propsub = form.save(commit=False)
            propsub.save()
            addressSplit = str(propsub.addressfull).split(',')
            address = addressSplit[0].rstrip()
            city = addressSplit[1].rstrip()
            city = city.lstrip()
            statezip = addressSplit[2].lstrip()
            statezip = statezip.split(' ')
            state = statezip[0]
            state = state.upper()
            zipcode = statezip[1]
            Property.objects.filter(pk=propsub.pk).update(usersub=request.user.username)
            Property.objects.filter(pk=propsub.pk).update(address=address)
            Property.objects.filter(pk=propsub.pk).update(city=city)
            Property.objects.filter(pk=propsub.pk).update(state=state)
            Property.objects.filter(pk=propsub.pk).update(zipcode=zipcode)
            for grp in usersNgroup:
                if grp == userName:
                    return redirect('rei_properties_edit', propsub.pk)
            return render(request, 'rei/rei_submitthanks.html', {})
    else:
        form = PropertyFormSub()
    return render(request, 'rei/rei_submit.html', {'form': form})

@login_required(login_url='/accounts/login/')
def rei_properties(request):
    props = Property.objects.all().order_by('state')
    detaillist = []
    for prop in props:
        #prop.zestimate = 0 if prop.zestimate == '' else prop.zestimate
        #down = DownPayment(prop.zestimate, prop.downpayment)
        #closingcost = ClosingCosts(prop.zestimate, prop.state)
        propCalc = PropListCalcs(prop)
        prop = propCalc[0]
        propview1yr = propCalc[1]
        detaildict = {
            'pk' : prop.pk,
            'address' : prop.address,
            'city' : prop.city,
            'state' : prop.state,
            'sales_price' : prop.sales_price,
            'rent_price' : propview1yr['expectedrent1m'],
            'totalinvestment' : propview1yr['totalinvestment'],
            'annreturn': propview1yr['annreturn'],
            'caprate': propview1yr['caprate'],
            'cashoncash': propview1yr['cashoncash'],
            'onepercentrule': propview1yr['onepercentrule'],
            'totalnetcf1y': propview1yr['totalnetcf1y'],
            'usersub' : prop.usersub,
            }
        detaillist.append(detaildict)
    return render(request, 'rei/rei_properties.html', {'detaillist': detaillist})

@login_required(login_url='/accounts/login/')
def rei_myproperties(request):
    props = Property.objects.filter(owned=request.user).order_by('state')
    detaillist = []
    for prop in props:
        #prop.zestimate = 0 if prop.zestimate == '' else prop.zestimate
        #down = DownPayment(prop.zestimate, prop.downpayment)
        #closingcost = ClosingCosts(prop.zestimate, prop.state)
        propCalc = PropListCalcs(prop)
        prop = propCalc[0]
        propview1yr = propCalc[1]
        detaildict = {
            'pk' : prop.pk,
            'address' : prop.address,
            'city' : prop.city,
            'state' : prop.state,
            'sales_price' : prop.sales_price,
            'rent_price' : propview1yr['expectedrent1m'],
            'totalinvestment' : propview1yr['totalinvestment'],
            'annreturn': propview1yr['annreturn'],
            'caprate': propview1yr['caprate'],
            'cashoncash': propview1yr['cashoncash'],
            'onepercentrule': propview1yr['onepercentrule'],
            'totalnetcf1y': propview1yr['totalnetcf1y'],
            'usersub' : prop.usersub,
            }
        detaillist.append(detaildict)
    return render(request, 'rei/rei_myproperties.html', {'detaillist': detaillist})
@login_required(login_url='/accounts/login/')
def rei_submitthanks(request):
    #Define a function to email me when someone submits a property.
    return render(request, 'rei/rei_submitthanks.html', {})

@login_required(login_url='/accounts/login/')
def rei_properties_view(request, pk):
    prop = Property.objects.get(pk=pk)
    propCalc = PropViewCalcs(prop)
    prop = propCalc[0]
    location = propCalc[1]
    googleapi_key = propCalc[2]
    propview1yr = propCalc[3]
    propview5yr = propCalc[4]
    propview10yr = propCalc[5]
    propview15yr = propCalc[6]
    if request.method == 'POST':
        form = PropertyFormNotes(request.POST, instance=prop)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.save(update_fields=['notes'])
            return redirect('rei_properties_view', pk=pk)
    else:
        form = PropertyFormNotes(instance=prop)
    return render(request, 'rei/rei_properties_view.html', {'prop': prop, 'form': form, 'location': location, \
                'googleapi_key': googleapi_key, 'propview1yr': propview1yr, 'propview5yr': propview5yr, \
                'propview10yr': propview10yr, 'propview15yr': propview15yr})

@login_required(login_url='/accounts/login/')
def rei_properties_view_print(request, pk):
    if not SiteConfig.objects.all():
        siteconfig = {'sitename': 'Business Name'}
    else:
        # Make sure to only have 1 object of SiteConfig in DB
        siteconfig = SiteConfig.objects.all().first()
    prop = Property.objects.get(pk=pk)
    propCalc = PropViewCalcs(prop)
    prop = propCalc[0]
    propview1yr = propCalc[3]
    propview5yr = propCalc[4]
    propview10yr = propCalc[5]
    propview15yr = propCalc[6]
    return render(request, 'rei/rei_properties_view_print.html', {'prop': prop, 'propview1yr': propview1yr, \
                'propview5yr': propview5yr, 'propview10yr': propview10yr, 'propview15yr': propview15yr, \
                'siteconfig': siteconfig})

@pdf_decorator
def rei_properties_view_pdf(request, pk):
    if not SiteConfig.objects.all():
        siteconfig = {'sitename': 'Business Name'}
    else:
        # Make sure to only have 1 object of SiteConfig in DB
        siteconfig = SiteConfig.objects.all().first()
    prop = Property.objects.get(pk=pk)
    propCalc = PropViewCalcs(prop)
    prop = propCalc[0]
    propview1yr = propCalc[3]
    propview5yr = propCalc[4]
    propview10yr = propCalc[5]
    propview15yr = propCalc[6]
    return render(request, 'rei/rei_properties_view_print.html', {'prop': prop, 'propview1yr': propview1yr, \
                'propview5yr': propview5yr, 'propview10yr': propview10yr, 'propview15yr': propview15yr, \
                'siteconfig': siteconfig})

@login_required(login_url='/accounts/login/')
def rei_properties_edit(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=prop)
        if form.is_valid():
            propnotes = form.save(commit=False)
            propnotes.save()
            return redirect('rei_properties_view', pk=pk)
    else:
        form = PropertyForm(instance=prop)
    return render(request, 'rei/rei_properties_edit.html', {'form': form})

@login_required(login_url='/accounts/login/')
def rei_properties_del(request, pk):
    Property.objects.get(pk=pk).delete()
    return redirect('rei_properties')

@login_required(login_url='/accounts/login/')
def rei_properties_update(request, pk):
    prop = Property.objects.get(pk=pk)
    RunFreeAPI(prop)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    #return redirect('rei_properties')

def rei_apihome(request):
    apistores = ApiStore.objects.all().order_by('name')
    return render(request, 'rei/rei_apihome.html', {'apistores': apistores})

@login_required(login_url='/accounts/login/')
def rei_apistore_add(request):
    if request.method == 'POST':
        form = ApiStoreForm(request.POST)
        if form.is_valid():
            apistore = form.save(commit=False)
            apistore.save()
            return redirect('rei_apihome')
    else:
        form = ApiStoreForm()
    return render(request, 'rei/rei_apistore_add.html', {'form': form})

@login_required(login_url='/accounts/login/')
def rei_apistore_edit(request, pk):
    apistore = get_object_or_404(ApiStore, pk=pk)
    if request.method == 'POST':
        form = ApiStoreForm(request.POST, instance=apistore)
        if form.is_valid():
            apistore = form.save(commit=False)
            apistore.save()
            return redirect('rei_apihome')
    else:
        form = ApiStoreForm(instance=apistore)
    return render(request, 'rei/rei_apistore_edit.html', {'form': form})

@login_required(login_url='/accounts/login/')
def rei_apistore_del(request, pk):
    ApiStore.objects.get(pk=pk).delete()
    return redirect('rei_apihome')