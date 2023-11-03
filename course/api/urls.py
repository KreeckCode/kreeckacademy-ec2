# course/urls.py
from django.urls import path
from .views import ProgramList, ProgramDetail, CourseList, CourseDetail, CourseAllocationList, CourseAllocationDetail

app_name = "courses-api"

urlpatterns = [
    path('programs/', ProgramList.as_view(), name='program-list'),
    path('programs/<int:pk>/', ProgramDetail.as_view(), name='program-detail'),
    path('courses/', CourseList.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetail.as_view(), name='course-detail'),
    path('course-allocations/', CourseAllocationList.as_view(), name='courseallocation-list'),
    path('course-allocations/<int:pk>/', CourseAllocationDetail.as_view(), name='courseallocation-detail'),
    path('course-levels/', CourseList.as_view(), name='courses-list'),
]