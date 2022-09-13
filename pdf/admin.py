from django.contrib import admin
import nested_admin
from .models import Pdffile
from api.models import Invoice, Meter
# Register your models here.

class PdffileyAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_max_show_all = 50
    list_display = ["pdf"]



class MeterInline(nested_admin.NestedTabularInline):
    model = Meter
    extra = 0

    fieldsets = (
        (
            "Meter Details",
            {
                "fields": (
                    "invoice",
                    "meter_no",
                    "meter_type",
                    "acc_description",
                    "this_reading",
                    "last_reading",
                    "consumption",
                    "average_rate",
                    "other_rate",
                    "consumption_period",
                    "amount_from_inv",
                    "from_date",
                    "to_date",
                ),
            },
        ),
    )

class InvoiceAdmin(nested_admin.SortableHiddenMixin, nested_admin.NestedModelAdmin):
    inlines = [
        MeterInline,
    ]

    fieldsets = (
        (
            "Invoice Details",
            {
                "fields": (
                    "inv_ref",
                    "description",
                    "supplier_code",
                    "supplier_name",
                    "invoice_date",
                    "due_date",
                    "total_invoice_amount",
                    "total_water_rate",
                    "total_water_usage",
                    "total_other_amount",
                ),
            },
        ),
    )
    list_per_page = 25
    list_max_show_all = 50
    list_display = ["inv_ref"]




admin.site.register(Pdffile, PdffileyAdmin)
admin.site.register(Invoice, InvoiceAdmin)