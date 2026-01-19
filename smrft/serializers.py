from rest_framework import serializers
from .models import CourseEnquiry, AlumniRegistration


from bson import ObjectId
class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        return ObjectId(data)

class CourseEnquirySerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    
    class Meta:
        model = CourseEnquiry
        fields = ['id', 'name', 'email', 'mobile', 'course', 'branch', 'message', 'created_at']

class AlumniRegistrationSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    
    class Meta:
        model = AlumniRegistration
        fields = '__all__'