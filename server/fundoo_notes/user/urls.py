from django.urls import path
# from .views import register_user,login_user

# urlpatterns = [
#     path("register/",register_user,name="register_user"),
#     path("login/",login_user,name="login_user")
# ]

from .views import RegisterUserView, LoginUserView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login')
]