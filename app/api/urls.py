from . import views

from django.urls import path

app_name = "dashboard-api"

urlpatterns = [
    path('semester/', views.SemesterListView.as_view(), name="semester-api"),
    path('session/', views.SessionListView.as_view(), name="session-api"),
    path('updates/', views.NewsListView.as_view(), name="news-api"),
    
]