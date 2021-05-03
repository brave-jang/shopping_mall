import csv
import datetime
from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Order, OrderItem


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpRequest(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}.csv.format(opts.verbose_name)'
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%Y-%m-%d")
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'


def order_detail(obj):
    url = reverse('order:admin_order_detail', args=[obj.id])
    html = mark_safe(f'<a href="{url}">Detail</a>')
    return html
order_detail.short_description = 'Detail'


def order_pdf(obj):
    url = reverse('order:admin_order_pdf', args=[obj.id])
    html = mark_safe(f'<a href="{url}">PDF</a>')
    return html
order_pdf.short_description = 'PDF'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # 검색 버튼


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid', order_detail, 'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline] 
    actions = [export_to_csv]

