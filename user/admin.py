from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin

from .models import Reservation, LogHistory

class ReservationAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

class LogHistoryAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

admin.site.register(Reservation, ReservationAdmin)

admin.site.register(LogHistory, LogHistoryAdmin)
