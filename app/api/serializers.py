
from rest_framework import serializers
from app.models import NewsAndEvents, Semester, Session

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsAndEvents
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'