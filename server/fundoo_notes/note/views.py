from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Notes
from .serializers import Noteserializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action

class NoteViewSet(viewsets.ModelViewSet):

    queryset = Notes.objects.all()
    serializer_class = Noteserializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        
        user = self.request.user
        return Notes.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        
        try:
            data = request.data
            data['user'] = request.user.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response({
                    "message": "Note created successfully.",
                    "status": "success",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED, headers=headers)
            
            return Response({
                "message": "Failed to create note.",
                "status": "failed",
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def update(self, request, *args, **kwargs):
       
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response({
                    "message": "Note updated successfully.",
                    "status": "success",
                    "data": serializer.data
                })
            
            return Response({
                "message": "Failed to update note.",
                "status": "failed",
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except NotFound:
            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to update does not exist."
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def destroy(self, request, *args, **kwargs):
       
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                "message": "Note deleted successfully.",
                "status": "success"
            }, status=status.HTTP_204_NO_CONTENT)

        except NotFound:
            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to delete does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


    @action(detail=True, methods=['patch'])
    def archive(self, request, pk=None):

        try:
            note = self.get_object()
            note.is_archive = True
            note.save()
            serializer = self.get_serializer(note)
            return Response({
                "message": "Note archived successfully.",
                "status": "success",
                "data": serializer.data
            })

        except NotFound:
            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to archive does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=False, methods=['get'])
    def is_archived(self, request):
    
        try:
            archived_notes = self.get_queryset().filter(is_archive=True)
            serializer = self.get_serializer(archived_notes, many=True)
            return Response({
                "message": "Archived notes retrieved successfully.",
                "status": "success",
                "data": serializer.data
            })
        
        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def trash(self, request, pk=None):
    
        try:
            note = self.get_object()
            note.is_trash = True
            note.save()
            serializer = self.get_serializer(note)
            return Response({
                "message": "Note trashed successfully.",
                "status": "success",
                "data": serializer.data
            })

        except NotFound:
            return Response({
                "message": "Note not found.",
                "status": "failed",
                "error": "The note you are trying to trash does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    @action(detail=False, methods=['get'])
    def is_trashed(self, request):

        try:
            trashed_notes = self.get_queryset().filter(is_trash=True)
            serializer = self.get_serializer(trashed_notes, many=True)
            return Response({
                "message": "Trashed notes retrieved successfully.",
                "status": "success",
                "data": serializer.data
            })
        
        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": "failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)