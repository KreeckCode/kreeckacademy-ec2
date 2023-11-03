# course/api_views.py
from rest_framework import generics
from course.models import Program, Course, CourseAllocation
from .serializers import ProgramSerializer, CourseSerializer, CourseAllocationSerializer
from rest_framework.permissions import AllowAny
from SMS.settings import DEBUG
from rest_framework.permissions import IsAuthenticated


class ProgramList(generics.ListCreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  # No authentication classes
        permission_classes = [AllowAny]  # Allow any user (no permissions required)
    

class ProgramDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  # No authentication classes
        permission_classes = [AllowAny]  # Allow any user (no permissions required)
    

class CourseList(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  # No authentication classes
        permission_classes = [AllowAny]  # Allow any user (no permissions required)
    

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  # No authentication classes
        permission_classes = [AllowAny]  # Allow any user (no permissions required)
    

class CourseAllocationList(generics.ListCreateAPIView):
    queryset = CourseAllocation.objects.all()
    serializer_class = CourseAllocationSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  # No authentication classes
        permission_classes = [AllowAny]  # Allow any user (no permissions required)
    

class CourseAllocationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseAllocation.objects.all()
    serializer_class = CourseAllocationSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  # No authentication classes
        permission_classes = [AllowAny]  # Allow any user (no permissions required)
    
