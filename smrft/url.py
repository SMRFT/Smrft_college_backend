from django.urls import path
from .views import get_events,get_file
from . import views
urlpatterns = [
    path('events/', get_events, name='get_events'),
    path('events/image/<str:file_id>/', get_file, name='serve_image'),  
    path('enquiry/', views.course_enquiry, name='course_enquiry'),
]
