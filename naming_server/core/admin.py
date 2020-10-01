from django.contrib import admin

from .models import __all__ as all_models

for _model in all_models:
    admin.site.register(_model)
