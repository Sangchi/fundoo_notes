from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Notes
from .serializers import Noteserializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from django.db import DatabaseError
from loguru import logger

class NoteViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, editing, archiving, and trashing user notes.

    desc: this handles CRUD operations and custom actions for user notes.
    """

    queryset = Notes.objects.all()
    serializer_class = Noteserializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        """
        desc: fetches all notes for the authenticated user.
        params: request The HTTP request object.
        return: QuerySet: filtered notes belonging to the user.
        """
        try:
            user = self.request.user
            note=Notes.objects.filter(user=user)
            logger.info("Successfully fetched notes for user.")
            return note
        
        except DatabaseError as e:
            logger.error(f"Database error while fetching notes: {e}")
            return Response(
                {
                    'message': 'Failed to fetch notes',
                    'status': 'error',
                    'errors': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error while fetching notes: {e}")
            return Response(
                {
                    'message': 'An unexpected error occurred',
                    'status': 'error',
                    'errors': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def create(self, request, *args, **kwargs):
        """
        desc: creates a new note instance for the authenticated user.
        params: request: the http request object containing note data.
        return: response: success or failure message with status code.
        """
        
        try:
            data = request.data
            data['user'] = request.user.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info("Note created successfully.")
                return Response({
                    "message": "Note created successfully.",
                    "status": "success",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED, headers=headers)
            
            logger.warning(f"Failed to create note. Validation errors: {serializer.errors}")
            return Response({
                "message": "Failed to create note.",
                "status": "failed",
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:

            logger.error(f"unnexpected error while creating the note {e}")

            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        

    def update(self, request, pk=None):
        """
        Update an existing note for the user.
        Parameters: request (Request) - HTTP request, pk (int) - Note ID.
        Returns: Serialized updated note data or error message.
        """
        try:
            note = Notes.objects.get(pk=pk, user=request.user)
        except NotFound:
            logger.warning("Attempted to update a note that does not exist.")

            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to archive does not exist."
            }, status=status.HTTP_404_NOT_FOUND)


        serializer = self.get_serializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Note successfully updated.")
            return Response({
            'message': 'Successfully updated',
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

        logger.warning(f"Validation error during note update: {serializer.errors}")
        return Response({
        'message': 'Validation error',
        'status': 'error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        desc: deletes a note instance.
        params: request : The HTTP request object.
        return: Response: success or failure message with status code.
        """
       
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            logger.info("Note deleted successfully.")
            return Response({
                "message": "Note deleted successfully.",
                "status": "success"
            }, status=status.HTTP_204_NO_CONTENT)

        except NotFound as e:
            logger.warning(f"Attempted to delete a note that does not exist: {e}")

            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to delete does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"unexpected error occurred ,when tried to delete data{e}.")
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    @action(detail=True, methods=['patch'])
    def archive(self, request, pk=None):
        """
        desc: archives a specific note instance.
        params: request: The HTTP request object.
        params: pk: Primary key of the note to be archived.
        return: response: success or failure message with status code.
        """

        try:
            note = self.get_object()
            note.is_archive = not note.is_archive
            note.save()
            serializer = self.get_serializer(note)
            logger.info("Note archived successfully.")
            return Response({
                "message": "Note archived successfully.",
                "status": "success",
                "data": serializer.data
            })

        except NotFound as e:
            logger.warning(f"Attempted to archive a note that does not exist: {e}")

            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to archive does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:

            logger.errror(f"unexpected error occurred while archivinng note {e}")

            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=False, methods=['get'])
    def is_archived(self, request):
        """
        desc: retrieves all archived notes.
        params: request: The HTTP request object.
        return: response: serialized list of archived notes or error message.
        """
    
        try:
            archived_notes = self.get_queryset().filter(is_archive=True,is_trash=False)
            serializer = self.get_serializer(archived_notes, many=True)
            logger.info("Archived notes retrieved successfully.")

            return Response({
                "message": "Archived notes retrieved successfully.",
                "status": "success",
                "data": serializer.data
            })
        
        except NotFound as e:
            logger.warning(f"Attempted to retrieve archived notes but none were found{e}.")

            return Response({
               "message":"archieve note not exist in database. " ,
               "status":"failed",
               "error":"trying to fetch is_archive note not exist in database."
            })
        
        except Exception as e:

            logger.error(f"unexpected error occurred while checking the archived note.")

            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def trash(self, request, pk=None):
        """
        desc: trashes a specific note instance.
        params: request : The HTTP request object.
        params: pk : Primary key of the note to be trashed.
        return: response: success or failure message with status code.
        """
    
        try:
            note = self.get_object()
            note.is_trash = not note.is_trash
            note.save()
            serializer = self.get_serializer(note)
            logger.info("Note trashed successfully.")
        
            return Response({
                "message": "Note trashed successfully.",
                "status": "success",
                "data": serializer.data
            })

        except NotFound as e:

            logger.warning(f"Attempted to trash a note that does not exist: {e}")

            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to trash does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:

            logger.error(f"unexpected error occurred while trashing the note.")

            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    @action(detail=False, methods=['get'])
    def is_trashed(self, request):
        """
        desc: retrieves all trashed notes.
        params: request : The HTTP request object.
        return: response: serialized list of trashed notes or error message.
        """

        try:
            trashed_notes = self.get_queryset().filter(is_trash=True)
            serializer = self.get_serializer(trashed_notes, many=True)
            logger.info(f"Note trashed retrive successfully")
            return Response({
                "message": "Trashed notes retrieved successfully.",
                "status": "success",
                "data": serializer.data
            })
        except NotFound as e:

            logger.warning(f"the trashed note not found in the database.")

            return Response({

                "message":"Note not Found error.",
                "status":"failed",
                "error":"note is not found in the database."
            })
        
        except Exception as e:

            logger.error(f"unexpected error occurred while finding the trashed note.")

            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
