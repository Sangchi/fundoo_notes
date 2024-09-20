from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.reverse import reverse
from .models import Users
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import jwt
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import AllowAny
from user.tasks import send_verification_email
from drf_yasg.utils import swagger_auto_schema


class RegisterUserView(APIView):
    permission_classes = ()
    authentication_classes = ()
    @swagger_auto_schema(operation_summary="register user", request_body=UserRegistrationSerializer, responses={200: UserRegistrationSerializer})
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
    
            token = RefreshToken.for_user(user).access_token
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
    
    @swagger_auto_schema(operation_summary='login user',request_body=UserLoginSerializer,responses={200:UserLoginSerializer})
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
         
            return Response({
                'message': 'User login successful',
                'status': 'success',
                'data': serializer.data
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = Users.objects.get(id=payload["user_id"])
        if not user.is_verified:
            user.is_verified = not user.is_verified
            user.save()

        return Response({
            'message': 'Email verified successfully',
            'status': 'success'
            }, status=status.HTTP_200_OK)

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
