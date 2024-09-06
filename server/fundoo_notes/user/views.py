from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from django.views.decorators.csrf import csrf_exempt


class RegisterUserView(APIView):
    @csrf_exempt
    def post(self, request):
    
        try:
            serializer = UserRegistrationSerializer(data=request.data)
    
            if serializer.is_valid():
                serializer.save()

                return Response({
                    "message": "User registered successfully",
                    "status": "success",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            else:

                return Response({
                    "message": "Validation error",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:

            return Response({
                "message": "An unexpected error occurred",
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class LoginUserView(APIView):

    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                user = authenticate(username=email, password=password)

                if user is not None:
                    user_data = UserRegistrationSerializer(user).data
                    return Response({
                        "message": "User logged in successfully",
                        "status": "success",
                        "data": user_data
                    }, status=status.HTTP_200_OK)
                
                return Response({
                    "message": "Invalid credentials",
                    "status": "error"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({
                "message": "Validation error",
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        
        except Exception as e:

            return Response({
                "message": "An unexpected error occurred",
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
