from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from loguru import logger
from .models import Label
from .serializers import LabelSerializer



class LabelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    A viewset for viewing, creating, updating, and deleting labels.
    Handles CRUD operations for user labels with JWT authentication and logging.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Label.objects.all()
    serializer_class = LabelSerializer

    def get_queryset(self):
        """
        Limits queryset to the authenticated user's labels.
        Returns a QuerySet filtered by the current user.
        """
        try:
            label=self.queryset.filter(user=self.request.user)
            
            return label
        except NotFound as e:
            logger.warning(f"the data not found in the database.")
            return Response({
                "message":"user not found",
                "status":"faield",
                "error":"data not found"

            })
        except Exception as e:
            return Response({

                "message":"unexpected error occured",
                "status":"faield",
                "error":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

    def create(self, request, *args, **kwargs):
        """
        Creates a new label for the authenticated user.
        Parameters:
            request (Request): The HTTP request object with label data.
        Returns:
            Response: Serialized label data or error message.
        """
        try:
            data = request.data.copy()
            data['user'] = request.user.id

            logger.info(f"Creating label with data: {data}")
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response({
                "message":"label created succcessfully",
                "status":"success",
                "data":serializer.data
                }, status=status.HTTP_201_CREATED, headers=headers)
        
        except ValidationError as e:
            logger.error(f"Validation error during label creation: {e}")
            return Response({
                'message': 'Validation error',
                'status': 'error',
                'errors': e.detail 
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as e:
            logger.error(f"Integrity error during label creation: {e}")
            return Response({
                'message': 'Database integrity error',
                'status': 'error',
                'errors': 'A required field is missing or contains invalid data. Please ensure all required fields are correctly filled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except DatabaseError as e:
            logger.error(f"Database error during label creation: {e}")
            return Response({
                'message': 'Database error',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:

            logger.error(f"Unexpected error during label creation: {e}")
            return Response({
                'message': 'An unexpected error occurred',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a specific label for the authenticated user.
        Parameters:
            request (Request): The HTTP request object.
            pk (int): Primary key of the label.
        Returns:
            Response: Serialized label data or error message.
        """
        try:
            return super().retrieve(request, *args, **kwargs)
        except ObjectDoesNotExist as e:
            logger.warning(f"Label not found during retrieval: {e}")
            return Response({
                'message': 'Label not found',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error during label retrieval: {e}")
            return Response({
                'message': 'An unexpected error occurred',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def update(self, request, *args, **kwargs):
        """
        Updates a specific label for the authenticated user.
        Parameters:
            request : The HTTP request object with label data.
            pk: Primary key of the label.
        Returns:
            Response: Serialized label data or error message.
        """
        try:
            label_instance = self.get_object()
            
            if label_instance.user != request.user:
                return Response({
                    'message': 'You do not have permission to update this label',
                    'status': 'error',
                    'errors': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data.copy()
            data['user'] = request.user.id
            
            serializer = self.get_serializer(label_instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({
                "message":"label updated succesfully",
                "status":"success",
                "data":serializer.data
            })
    
        except ValidationError as e:
            logger.error(f"Validation error during label update: {e}")
            return Response({
                'message': 'Validation error',
                'status': 'error',
                'errors': e.detail  # type: ignore
            }, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            logger.error(f"Integrity error during label update: {e}")
            return Response({
                'message': 'Database integrity error',
                'status': 'error',
                'errors': 'A required field is missing or contains invalid data. Please ensure all required fields are correctly filled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except DatabaseError as e:
            logger.error(f"Database error during label update: {e}")
            return Response({
                'message': 'Database error',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"Unexpected error during label update: {e}")
            return Response({
                'message': 'An unexpected error occurred',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a specific label for the authenticated user.
        Parameters:
            request: The HTTP request object.
            pk: Primary key of the label.
        Returns:
            Response: Empty response or error message.
        """
        try:
            lable=super().destroy(request, *args, **kwargs)
            return  Response({
                "message":"label deleted successfully",
                "status":"success",
                "data":lable.data
            })
        
        except ObjectDoesNotExist as e:
            logger.warning(f"Label not found during deletion: {e}")
            return Response({
                'message': 'Label not found',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        except DatabaseError as e:
            logger.error(f"Database error during label deletion: {e}")
            return Response({
                'message': 'Database error',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error during label deletion: {e}")
            return Response({
                'message': 'An unexpected error occurred',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def list(self, request, *args, **kwargs):
        """
        Fetches all labels for the authenticated user.
        Parameters:
            request : The HTTP request object.
        Returns:
            Response: Serialized list of labels or error message.
        """
        try:
            label=super().list(request, *args, **kwargs)
            return Response({
                "message":"successfully retrive label",
                "status":"success",
                "data":label.data
            })
        except DatabaseError as e:
            logger.error(f"Database error during label listing: {e}")
            return Response({
                'message': 'Database error',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error during label listing: {e}")
            return Response({
                'message': 'An unexpected error occurred',
                'status': 'error',
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
