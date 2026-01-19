from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from pymongo import MongoClient
from bson import ObjectId
import gridfs
from urllib.parse import quote_plus
import json
import logging
from .models import CourseEnquiry, AlumniRegistration
from .serializers import CourseEnquirySerializer, AlumniRegistrationSerializer
import os 
# Logger Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('smrft.log')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# MongoDB Connection Helper
def get_db():
    client = MongoClient(os.getenv("DB_HOST"))
    return client.College

# --- Event Views ---

@api_view(['GET'])
def get_events(request):
    db = get_db()
    uploads_collection = db['uploads']
    files_collection = db['fs.files']

    try:
        events = uploads_collection.find()
        event_list = []

        for event in events:
            file_id = event.get('file_id')
            
            if file_id:
                file_info = files_collection.find_one({"_id": file_id})
                if file_info:
                    event_data = {
                        "_id": str(event["_id"]),
                        "title": event["title"],
                        "startDate": event["startDate"],
                        "endDate": event["endDate"],
                        "description": event.get("description", ""),
                        "file": {
                            "filename": file_info["filename"],
                            "uploadDate": file_info["uploadDate"],
                            "md5": file_info["md5"],
                            "chunkSize": file_info["chunkSize"],
                            "length": file_info["length"],
                            "file_id": str(file_id)
                        }
                    }
                    event_list.append(event_data)

        logger.info('Events retrieved successfully')
        return JsonResponse(event_list, safe=False)
    except Exception as e:
        logger.error(f'Error retrieving events: {str(e)}')
        return JsonResponse({'error': 'Failed to retrieve events'}, status=500)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_event(request):
    try:
        title = request.data.get('title')
        start_date = request.data.get('startDate')
        end_date = request.data.get('endDate')
        description = request.data.get('description', '')
        image = request.FILES.get('image')

        if not title or not image:
            return JsonResponse({'error': 'Title and Image are required'}, status=400)

        db = get_db()
        fs = gridfs.GridFS(db)
        uploads_collection = db['uploads']

        # Save image to GridFS
        file_id = fs.put(image, filename=image.name)

        # Save event metadata to uploads collection
        event_data = {
            "title": title,
            "startDate": start_date,
            "endDate": end_date,
            "description": description,
            "file_id": file_id
        }
        
        result = uploads_collection.insert_one(event_data)

        logger.info(f'Event added successfully: {result.inserted_id}')
        return JsonResponse({'message': 'Event added successfully', 'id': str(result.inserted_id)}, status=201)

    except Exception as e:
        logger.error(f'Error adding event: {str(e)}')
        return JsonResponse({'error': f'Failed to add event: {str(e)}'}, status=500)

@api_view(['DELETE'])
def delete_event(request, event_id):
    try:
        db = get_db()
        uploads_collection = db['uploads']
        fs = gridfs.GridFS(db)

        event = uploads_collection.find_one({"_id": ObjectId(event_id)})
        
        if not event:
            return JsonResponse({'error': 'Event not found'}, status=404)

        # Delete file from GridFS
        if 'file_id' in event:
            fs.delete(event['file_id'])

        # Delete event document
        uploads_collection.delete_one({"_id": ObjectId(event_id)})

        logger.info(f'Event deleted successfully: {event_id}')
        return JsonResponse({'message': 'Event deleted successfully'}, status=200)

    except Exception as e:
        logger.error(f'Error deleting event: {str(e)}')
        return JsonResponse({'error': 'Failed to delete event'}, status=500)

@api_view(['GET'])
def get_file(request, file_id):
    db = get_db()
    fs = gridfs.GridFS(db)

    try:
        file_id_obj = ObjectId(file_id)
        file_data = fs.find_one({"_id": file_id_obj})
        
        if file_data:
            response = HttpResponse(file_data.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename={file_data.filename}'
            return response
        else:
            return HttpResponse(status=404)
    except Exception as e:
        logger.error(f'Error retrieving file {file_id}: {str(e)}')
        return HttpResponse(status=404)

# --- Enquiry Views ---

@api_view(['POST'])
def course_enquiry(request):
    serializer = CourseEnquirySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_enquiries(request):
    try:
        enquiries = CourseEnquiry.objects.all().order_by('-created_at')
        serializer = CourseEnquirySerializer(enquiries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error retrieving enquiries: {str(e)}')
        return Response({'error': 'Failed to fetch enquiries'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Alumni Views ---

@api_view(['POST'])
def register_alumni(request):
    try:
        serializer = AlumniRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Alumni registered successfully!'}, status=201)
        return JsonResponse({'message': 'Validation failed', 'errors': serializer.errors}, status=400)
    except Exception as e:
        logger.error(f'Error registering alumni: {str(e)}')
        return JsonResponse({'message': f'Failed to register: {str(e)}'}, status=500)

@api_view(['GET'])
def get_alumni_list(request):
    try:
        alumni = AlumniRegistration.objects.all().order_by('-created_at')
        serializer = AlumniRegistrationSerializer(alumni, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f'Error retrieving alumni: {str(e)}')
        return Response({'error': 'Failed to fetch alumni list'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
