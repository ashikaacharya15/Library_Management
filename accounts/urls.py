from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('all', views.display, name='display'),
    path('checkin', views.checkin, name='checkin'),
    path('create', views.create, name="create"),
    path('fines', views.fines, name="fines"),
    path('payfine', views.payfine, name="payfine"),
    path('updatefine', views.updatefine, name="updatefine"),
    re_path('^borrower/(.*)$', views.borrower, name='borrower'),
    re_path('^borrow/(.*)$', views.borrow, name='borrow'),
    re_path('^checkedin/(.*)$', views.checkedin, name='checkedin'),

]