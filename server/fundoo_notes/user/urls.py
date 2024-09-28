from django.urls import path
from .views import RegisterUserView, LoginUserView ,verify_registered_user
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('verify/<token>/',verify_registered_user,name='verify')
]