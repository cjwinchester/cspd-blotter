from django.contrib import admin
from blotter.models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('incident_datetime', 'title', 'division', 'location',)
