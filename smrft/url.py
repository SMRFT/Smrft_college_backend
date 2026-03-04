from django.urls import path
from .views import get_events, get_file, add_event, delete_event, get_enquiries, course_enquiry, register_alumni, get_alumni_list
from . import views

urlpatterns = [
    path('events/', get_events, name='get_events'),
    path('events/add/', add_event, name='add_event'),
    path('events/delete/<str:event_id>/', delete_event, name='delete_event'),
    path('events/image/<str:file_id>/', get_file, name='serve_image'),  
    path('enquiry/', course_enquiry, name='course_enquiry'),
    path('enquiries/', get_enquiries, name='get_enquiries'),
    path('register/', register_alumni, name='register_alumni'),
    path('alumni/', get_alumni_list, name='get_alumni_list'),
]
