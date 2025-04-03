from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from pymongo import MongoClient
from bson import ObjectId
import gridfs
from urllib.parse import quote_plus
import json


# Connect to MongoDB



def get_events(request):
    password = quote_plus('Smrft@2024')  # Update password as needed
    client = MongoClient(f'mongodb://admin:ifS2nTs6vm@103.205.141.208:27017/Lab?authSource=admin')
    db = client.College # The database in MongoDB
    fs = gridfs.GridFS(db)  # Initialize GridFS to store files

    uploads_collection = db['uploads']
    files_collection = db['fs.files']

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
                    "file": {
                        "filename": file_info["filename"],
                        "uploadDate": file_info["uploadDate"],
                        "md5": file_info["md5"],
                        "chunkSize": file_info["chunkSize"],
                        "length": file_info["length"],
                        "file_id": str(file_id)  # Include the file_id for image URL
                    }
                }
                event_list.append(event_data)

    return JsonResponse(event_list, safe=False)


import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and a stream handler
file_handler = logging.FileHandler('smrft.log')
stream_handler = logging.StreamHandler()

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def get_events(request):
    password = quote_plus('Smrft@2024')  # Update password as needed
    client = MongoClient(f'mongodb://admin:ifS2nTs6vm@103.205.141.208:27017/Lab?authSource=admin')
    db = client.College # The database in MongoDB
    fs = gridfs.GridFS(db)  # Initialize GridFS to store files

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
                        "file": {
                            "filename": file_info["filename"],
                            "uploadDate": file_info["uploadDate"],
                            "md5": file_info["md5"],
                            "chunkSize": file_info["chunkSize"],
                            "length": file_info["length"],
                            "file_id": str(file_id)  # Include the file_id for image URL
                        }
                    }
                    event_list.append(event_data)

        logger.info('Events retrieved successfully')
        return JsonResponse(event_list, safe=False)
    except Exception as e:
        logger.error(f'Error retrieving events: {str(e)}')
        return JsonResponse({'error': 'Failed to retrieve events'}, safe=False)


# Endpoint to serve files from GridFS
@api_view(['GET'])
def get_file(request, file_id):
    password = quote_plus('Smrft@2024')  # Update password as needed
    client = MongoClient(f'mongodb://admin:ifS2nTs6vm@103.205.141.208:27017/Lab?authSource=admin')
    db = client.College # The database in MongoDB
    fs = gridfs.GridFS(db)  # Initialize GridFS to store files

    # Assuming 'file_id' is passed in the URL
    file_id = ObjectId(file_id)  # Convert the string ID to ObjectId
    try:
        file_data = fs.find_one({"_id": file_id})
        
        if file_data:
            logger.info(f'File {file_data.filename} retrieved successfully')
            response = HttpResponse(file_data.read(), content_type='image/png')  # Change content_type if needed
            response['Content-Disposition'] = f'attachment; filename={file_data.filename}'
            return response
        else:
            logger.error(f'File {file_id} not found')
            return HttpResponse(status=404)
    except Exception as e:
        logger.error(f'Error retrieving file {file_id}: {str(e)}')
        return HttpResponse(status=404)
# Endpoint to serve files from GridFS
@api_view(['GET'])
def get_file(request, file_id):
    password = quote_plus('Smrft@2024')  # Update password as needed
    client = MongoClient(f'mongodb://admin:ifS2nTs6vm@103.205.141.208:27017/Lab?authSource=admin')
    db = client.College # The database in MongoDB
    fs = gridfs.GridFS(db)  # Initialize GridFS to store files

    # Assuming 'file_id' is passed in the URL
    file_id = ObjectId(file_id)  # Convert the string ID to ObjectId
    file_data = fs.find_one({"_id": file_id})
    
    if file_data:
        response = HttpResponse(file_data.read(), content_type='image/png')  # Change content_type if needed
        response['Content-Disposition'] = f'attachment; filename={file_data.filename}'
        return response
    return HttpResponse(status=404)



from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import CourseEnquiry
from .serializers import CourseEnquirySerializer

@api_view(['POST'])
def course_enquiry(request):
    serializer = CourseEnquirySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)