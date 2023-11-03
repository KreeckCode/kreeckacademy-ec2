from rest_framework import generics
from .serializers import NewsSerializer, SemesterSerializer, SessionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from SMS.settings import DEBUG
from app.models import NewsAndEvents, Semester, Session

class NewsListView(generics.ListCreateAPIView):
    queryset = NewsAndEvents.objects.all()
    serializer_class = NewsSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  # No authentication classes
        permission_classes = [AllowAny]  # Allow any user (no permissions required)
    


class SemesterListView(generics.ListCreateAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  
        permission_classes = [AllowAny]  


class SessionListView(generics.ListCreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    if DEBUG == False:
        permission_classes = [IsAuthenticated]
    else:
        authentication_classes = []  
        permission_classes = [AllowAny] 
    
