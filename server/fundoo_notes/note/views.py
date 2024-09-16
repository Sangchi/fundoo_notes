from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from django.db import DatabaseError
from loguru import logger
from .models import Notes
from .serializers import Noteserializers
from utils.redis_util import RedisUtils  # Import the RedisUtils class

class NoteViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, editing, archiving, and trashing user notes.

    desc: this handles CRUD operations and custom actions for user notes.
    """

    queryset = Notes.objects.all()
    serializer_class = Noteserializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
     
    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            cache_key =user.id
            cached_notes = RedisUtils.get(cache_key)
            if cached_notes is None:
                notes = Notes.objects.filter(user=user)
                serializer = self.get_serializer(notes, many=True)
                data = serializer.data
                RedisUtils.save(cache_key, data, timeout=3600)
            else:
                data = cached_notes

            logger.info("Notes list retrieved successfully.")
            return Response({
            "message": "Notes list retrieved successfully.",
            "status": "success",
            "data": data
             })

        except Exception as e:
            logger.error(f"Unexpected error occurred while retrieving notes list: {e}")
            return Response({
            "message": "An unexpected error occurred.",
            "status": "failed",
            "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create(self, request, *args, **kwargs):
        """
        Creates a new note instance for the authenticated user.
        """
        try:
            data = request.data
            data['user'] = request.user.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                notes=RedisUtils.get(request.user.id)
                if not notes:
                    notes=[serializer.data]
                else:
                    notes.append(serializer.data)

                RedisUtils.save(request.user.id, notes)
    
                
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
            logger.error(f"Unexpected error while creating the note: {e}")
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def update(self, request, pk=None):
        """
        Update an existing note for the user.
        """
        try:
            note = Notes.objects.get(pk=pk, user=request.user)
        except NotFound:
            logger.warning("Attempted to update a note that does not exist.")
            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to update does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            cache_key = request.user.id
            cached_notes = RedisUtils.get(cache_key)
        
            if cached_notes:
                cached_notes_dict = {note['id']: note for note in cached_notes}
                updated_note_data = serializer.data
                cached_notes_dict[updated_note_data['id']] = updated_note_data

                updated_cached_notes = list(cached_notes_dict.values())
                RedisUtils.save(cache_key, updated_cached_notes)

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
        Deletes a note instance.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)

            
            cache_key =request.user.id
            RedisUtils.delete(cache_key)

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

            logger.error(f"Unexpected error occurred while deleting the note: {e}")
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def archive(self, request, pk=None):
        """
        Archives a specific note instance.
        """
        try:
            note = self.get_object()
            note.is_archive = not note.is_archive
            note.save()
            serializer = self.get_serializer(note)

            cache_key=request.user.id 
            cache_notes=RedisUtils.get(cache_key)

            if cache_notes:
                updated_data=serializer.data
                updated_note=[n for n in cache_notes if n['id']!=updated_data['id']]
                updated_note.append(updated_data)

                RedisUtils.save(cache_key,updated_note,timeout=3600)


            logger.info("Note archived successfully and cache updated.")
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
            logger.error(f"Unexpected error occurred while archiving the note: {e}")
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def is_archived(self, request):
        """
        Retrieves all archived notes.
        """
        try:
            cache_key = request.user.id
            archived_notes = RedisUtils.get(cache_key)

            if archived_notes is None:
                archived_notes = self.get_queryset().filter(is_archive=True, is_trash=False)
                serializer = self.get_serializer(archived_notes, many=True)
                archived_notes = serializer.data
                RedisUtils.save(cache_key, archived_notes, timeout=3600)

            logger.info("Archived notes retrieved successfully.")
            return Response({
                "message": "Archived notes retrieved successfully.",
                "status": "success",
                "data": archived_notes
            })
        
        except NotFound as e:
            logger.warning(f"Attempted to retrieve archived notes but none were found: {e}.")
            return Response({
               "message": "Archived notes do not exist in the database.",
               "status": "failed",
               "error": "Trying to fetch archived notes, but they do not exist in the database."
            })
        
        except Exception as e:
            logger.error(f"Unexpected error occurred while checking archived notes: {e}.")
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=True, methods=['patch'])
    def trash(self, request, pk=None):
        """
        Trashes a specific note instance.
        """
        try:
            serializer= self.get_object()
            serializer.is_trash = not serializer.is_trash
            serializer.save()

            cache_key=request.user.id
            cache_notes=RedisUtils.get(cache_key)

            if cache_notes:
                updated_note_data=self.get_serializer(serializer).data
                updated_notes = [n for n in cache_notes if n['id'] != updated_note_data['id']]
                updated_notes.append(updated_note_data)
                RedisUtils.save(cache_key, updated_notes, timeout=3600)

            logger.info("Note trashed successfully and cache updated.")
            return Response({
                "message": "Note trashed successfully.",
                "status": "success",
                "data": self.get_serializer(serializer).data
            })

        except NotFound as e:
            logger.warning(f"Attempted to trash a note that does not exist: {e}")
            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to trash does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Unexpected error occurred while trashing the note: {e}")
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=False, methods=['get'])
    def is_trashed(self, request):
        """
        Retrieves all trashed notes.
        """
        try:
            cache_key = request.user.id
            trashed_notes = RedisUtils.get(cache_key)

            if trashed_notes is None:
                trashed_notes = self.get_queryset().filter(is_trash=True)
                serializer = self.get_serializer(trashed_notes, many=True)
                trashed_notes = serializer.data
                RedisUtils.save(cache_key, trashed_notes, timeout=3600)  # Cache for 1 hour
            else:
                trashed_notes=trashed_notes
            logger.info("Trashed notes retrieved successfully from cache .")
            return Response({
                "message": "Trashed notes retrieved successfully.",
                "status": "success",
                "data": trashed_notes
            })
        
        except NotFound as e:
            logger.warning(f"Attempted to retrieve trashed notes but none were found: {e}.")
            return Response({
                "message": "Trashed notes do not exist in the database.",
                "status": "failed",
                "error": "Trying to fetch trashed notes, but they do not exist in the database."
            })
        
        except Exception as e:
            logger.error(f"Unexpected error occurred while checking trashed notes: {e}.")
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
