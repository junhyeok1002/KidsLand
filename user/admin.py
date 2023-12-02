from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin

from .models import Reservation, LogHistory, DisableDay, Admin_Phone, Agree_Term

class ReservationAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

class LogHistoryAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

class DisableDayAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

class Admin_PhoneAdmin(ImportExportMixin, admin.ModelAdmin):
    pass

class Agree_TermsAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


admin.site.register(Reservation, ReservationAdmin)

admin.site.register(LogHistory, LogHistoryAdmin)

admin.site.register(DisableDay, DisableDayAdmin)

admin.site.register(Admin_Phone, Admin_PhoneAdmin)

admin.site.register(Agree_Term, Agree_TermsAdmin)