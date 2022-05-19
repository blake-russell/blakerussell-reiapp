"""blakerussell URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/signup/$', views.signup, name='signup'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^rei_dashboard/$', views.rei_dashboard, name='rei_dashboard'),
    url(r'^rei_submit/$', views.rei_submit, name='rei_submit'),
    url(r'^rei_myproperties/$', views.rei_myproperties, name='rei_myproperties'),
    url(r'^rei_properties/$', views.rei_properties, name='rei_properties'),
    url(r'^rei_properties/view/(?P<pk>[0-9]{1,10})/$', views.rei_properties_view, name='rei_properties_view'),
    url(r'^rei_properties/edit/(?P<pk>[0-9]{1,10})/$', views.rei_properties_edit, name='rei_properties_edit'),
    url(r'^rei_properties/del/(?P<pk>[0-9]{1,10})/$', views.rei_properties_del, name='rei_properties_del'),
    url(r'^rei_properties/update/(?P<pk>[0-9]{1,10})/$', views.rei_properties_update, name='rei_properties_update'),
    url(r'^rei_properties/view/print/(?P<pk>[0-9]{1,10})/$', views.rei_properties_view_print, name='rei_properties_view_print'),
    url(r'^rei_properties/view/pdf/(?P<pk>[0-9]{1,10})/$', views.rei_properties_view_pdf, name='rei_properties_view_pdf'),
    url(r'^rei_submitthanks/', views.rei_submitthanks, name='rei_submitthanks'),
    url(r'^rei_apihome/$', views.rei_apihome, name='rei_apihome'),
    url(r'^rei_apistore/add/$', views.rei_apistore_add, name='rei_apistore_add'),
    url(r'^rei_apistore/edit/(?P<pk>[0-9]{1,10})/$', views.rei_apistore_edit, name='rei_apistore_edit'),
    url(r'^rei_apistore/del/(?P<pk>[0-9]{1,10})/$', views.rei_apistore_del, name='rei_apistore_del'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
