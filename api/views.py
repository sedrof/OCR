from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView
from django.forms.models import inlineformset_factory, modelformset_factory
from django.db.models import Q
from pdf_gen.form import PdffileForm
from .models import Invoice, Meter
from .form import InvoiceEditForm, MeterEditForm

# Create your views here.


@login_required
def invoice_list_view(request):
    user = request.user
    invoices = Invoice.objects.all()
    invoice_paginator = Paginator(invoices, 20)
    form = PdffileForm()
    if request.method == "POST":
        form = PdffileForm(request.POST, request.FILES)
        print(form.is_valid())
        # if form is not valid then form data will be sent back to view to show error message
        if form.is_valid():
            form.save()
            return redirect("invoices:list")
    # return render(request, "home.html", {'form': form})

    page_number = request.GET.get("page")
    page = invoice_paginator.get_page(page_number)
    num_pages = invoice_paginator.num_pages

    return render(
        request,
        "invoices/invoice_list.html",
        {"page": page, "num_pages": num_pages, "form": form},
    )


@login_required
def invoice_create_view(request):
    form = InvoiceEditForm(request.POST or None)
    context = {"form": form}
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect(obj.get_absolute_url())
    return render(request, "invoices/create-update.html", context)


@login_required
def invoice_update_view(request, id=None):
    obj = get_object_or_404(Invoice, id=id)
    form = InvoiceEditForm(request.POST or None, instance=obj)
    MeterFormset = modelformset_factory(Meter, form=MeterEditForm, extra=0)
    qs = obj.meters.all()
    formset = MeterFormset(request.POST or None, queryset=qs)

    context = {
        "form": form,
        "formset": formset,
        "object": obj,
    }

    if all([form.is_valid(), formset.is_valid()]):
        # if form.is_valid():
        parent = form.save(commit=False)
        parent.save()
        for form in formset:
            child = form.save(commit=False)
            child.invoice = parent
            child.save()

    if request.htmx:
        return render(request, "partials/form-htmx.html", context)
    return render(request, "invoices/create-update.html", context)


@login_required
def delete_invoice(request, id):
    invoice = Invoice.objects.get(pk=id)
    invoice.delete()
    # messages.success(request, 'Expense removed')
    return redirect("invoices:list")
