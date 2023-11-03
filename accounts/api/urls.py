from . import views

from django.urls import path

app_name = "accounts-api"

urlpatterns = [
    path('users/', views.UserListView.as_view(), name="users-api"),
]