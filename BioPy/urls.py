"""BioPy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from BioPyApp import views

urlpatterns = [

    path('',views.HomePageView.as_view(),name="index"),

    path('home/',views.HomeView.as_view(),name="home"),

    path('contacts/',views.ContactsView.as_view(),name="contacts"), 

    path('terms/',views.TermsView.as_view(),name="terms"),

    path('about/',views.AboutView.as_view(),name="about"),

    path('goodbye/',views.GoodbyeView.as_view(),name="goodbye"),

    path('admin/', admin.site.urls,name="admin"),

    path('accounts/', include('allauth.urls')),

    # Newletter

    path('newsletter/',include('newsletter.urls')),

    # General

    path('processes/', views.ProcessList.as_view()),

    path('processes/<pk>/', views.ProcessDetail.as_view()),

    path('batches/', views.BatchList.as_view()),

    path('batches/<pk>/', views.BatchDetail.as_view()),

    path('variables/', views.VariableList.as_view()),

    path('variables/<pk>/', views.VariableDetail.as_view()),

    path('events/', views.EventList.as_view()),

    path('events/<pk>/', views.EventDetail.as_view()),

    path('classes/', views.ClassList.as_view()),

    path('classes/<pk>/', views.ClassDetail.as_view()),
]
