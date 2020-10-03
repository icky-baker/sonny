# import django.contrib.auth.urls
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dfs/", views.dfs, name="dfs"),
]
