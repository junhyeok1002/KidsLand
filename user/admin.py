from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin

from .models import Reservation, SessionDB

class ReservationAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

class SessionDBAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

admin.site.register(Reservation, ReservationAdmin)

admin.site.register(SessionDB, SessionDBAdmin)
