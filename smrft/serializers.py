from rest_framework import serializers
from .models import CourseEnquiry

class CourseEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnquiry
        fields = ['id', 'name', 'email', 'mobile', 'course', 'branch', 'created_at']