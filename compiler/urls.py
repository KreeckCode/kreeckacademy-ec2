from django.urls import path
from . import views

urlpatterns = [
    path('run_code/', views.run_code_view, name='run_code'),
]
