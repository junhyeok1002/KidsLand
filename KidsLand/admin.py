from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportMixin, ImportMixin

from user.models import Reservation

# admin.site.register(Reservation)