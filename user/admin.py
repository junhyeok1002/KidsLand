from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin

from .models import Reservation

class ReservationAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

admin.site.register(Reservation, ReservationAdmin)