
from django.urls import path, include
from .views import *

app_name='invoices'

urlpatterns = [
    path('invoice_list_view/', invoice_list_view,name='list'),
    path('create/', invoice_create_view,name='create'),
    path("<int:id>/edit/", invoice_update_view, name='update'),
    path('invoice-delete/<int:id>', delete_invoice, name="invoice-delete"),

]