from django.forms import model_to_dict
from django.shortcuts import render
from django.http import JsonResponse
from .models import Users
import json
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate
import re

# Create your views here.
#register
@require_POST
def register_user(request):

    try:
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return JsonResponse({
                "message": "[username,email,]",
                "status": "error"
                }, status=400)
        
        # Validate username
        if not isinstance(username, str):
            return JsonResponse({
                "message": "Username must be a string",
                "status": "error"
            }, status=400)
        
        # Validate email for ending with gmail.com after '@'
        email = email.lower()
        email_regex = r'^[a-z0-9._%+-]+@[a-z0-9]+\.[a-z]{2,}$'
        if not re.match(email_regex, email):
            return JsonResponse({
                "message": "Email must be a valid domain address",
                "status": "error"
            }, status=400)
        
        #password lenth should be minimum 8
        if len(password) < 8:
            return JsonResponse({
                "message": "Password must be at least 8 characters long",
                "status": "error"
            }, status=400)

        if Users.objects.filter(username=username).exists():
            return JsonResponse({
                "message": "user allready exist",
                "status": "error"
                }, status=400)

        user = Users.objects.create_user(username=username, email=email, password=password)
        user_data = model_to_dict(user)

        return JsonResponse({
            "message": "User registered successfully",
            "status": "success",
            "data": user_data
        }, status=201)

    except Exception as e:
        return JsonResponse({"message": "Unexpected error occured", "error": str(e)}, status=500)


#login
@require_POST
def login_user(request):

    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email and not password:
            return JsonResponse({
                "message": "email and password required",
                "status": "error"
                }, status=400)

        user = authenticate(username=email, password=password)
        user_data=model_to_dict(user)
        if user is not None:
            return JsonResponse({
                "message": "User logined successfully",
                "status": "success",
                "data":user_data
                }, status=201)

        else:
            return JsonResponse({
                "message": "invalid username and password",
                "status": "error"
                }, status=401)

    except json.JSONDecodeError:
        return JsonResponse({
            "message": "invalid JSON",
            "status": "error"
            }, status=400)




