from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.reverse import reverse
from datetime import datetime, timedelta, timezone
from .models import Users
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import AllowAny
from user.tasks import send_verification_email
from drf_yasg.utils import swagger_auto_schema
from rest_framework.throttling import UserRateThrottle ,  AnonRateThrottle
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout


class RegisterUserView(APIView):
    permission_classes = ()
    authentication_classes = ()
    throttle_classes = [AnonRateThrottle]
    @swagger_auto_schema(operation_summary="register user", request_body=UserRegistrationSerializer, responses={200: UserRegistrationSerializer})
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            payload = {
                  'user_id': user.id,
                  'exp': datetime.now(tz=timezone.utc)+ timedelta(hours=24),
                  'iat': datetime.now(tz=timezone.utc)
                }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            link = request.build_absolute_uri(reverse('verify', args=[token]))

            # send verification link asynchronously

            send_verification_email.delay(user.email, link)

            return Response({
                'message': 'User registered successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'message': 'Invalid data',
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):

    permission_classes = ()
    authentication_classes = ()
    
    throttle_classes = [UserRateThrottle]
    
    @swagger_auto_schema(operation_summary='login user',request_body=UserLoginSerializer,responses={200:UserLoginSerializer})
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            return Response({
                    "message": "User logged in successfully",
                    "status": "success",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Invalid data',
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['GET'])
@permission_classes([AllowAny])
def verify_registered_user(request, token):
    try:
       
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(token)
        user = Users.objects.get(id=decoded_token['user_id'])
        user.is_verified = True
        user.save()
        
       
        return Response({
            "message": "Token is valid",
            "status": "success",
            "data": decoded_token,
        },status=status.HTTP_202_ACCEPTED)

    except jwt.ExpiredSignatureError:
        return Response({
            'message': 'Token has expired',
            'status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except jwt.InvalidTokenError:
        return Response({
            'message': 'Invalid token',
            'status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)

    except Users.DoesNotExist:
        return Response({
            'message': 'User not found',
            'status': 'error'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'message': 'An unexpected error occurred',
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)



def register_view(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, "Registration failed. Please try again.")
    
    return render(request, 'registration.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')  
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'login.html')


def home_view(request):
    if request.user.is_authenticated:
        users = Users.objects.all()  
        return render(request, 'index.html', {'users': users})
    else:
        return redirect('login')  
    

def logout_view(request):
    logout(request)
    return redirect('login')