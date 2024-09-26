import pytest
from rest_framework.reverse import reverse
from user.models import Users
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.mark.django_db
def test_user_register_api_success(client):
    data={
        "username":"Tuddbnberuryggj",
        "email":"tuksdfccvcnfehehjjkr@gmail.com",
        "password":"tukavjjbmbvvbnnb"
       }
    
    url=reverse('register')
    response=client.post(path=url,data=data,content_type='application/json')
    assert response.status_code ==201
    
@pytest.mark.django_db
def test_user_register_api_already_registered(client):

    data = {
        "username":"Tuddbnberuryggj",
        "email":"tuksdfccvcnfehehjjkr@gmail.com",
        "password":"tukavjjbmbvvbnnb"
    }
    
    url = reverse('register')
    response=client.post(path=url, data=data, content_type='application/json')
    response = client.post(path=url, data=data, content_type='application/json')
    assert response.status_code == 400

@pytest.mark.django_db 
def test_user_registration_missing_fields(client):

    data={
         "email":"tuksdfccvcnfhjkkehjjkr@gmail.com",
        "password":"tukavjjbdbmdsjnb"
    }

    url=reverse('register')
    response=client.post(path=url,data=data,content_type='application/json')
    assert response.status_code==400


@pytest.mark.django_db 
def test_user_registration_missing_all_fields(client):

    data={
         
    }

    url=reverse('register')
    response=client.post(path=url,data=data,content_type='application/json')
    assert response.status_code==400


@pytest.mark.django_db
def test_user_register_invalid_username(client):

    data={
        "username":"tuddbnberuryggj",
        "email":"tuksdfccbnbmjkr@gmail.com",
        "password":"tukavjjbmdsafs"

    }

    url=reverse('register')
    response=client.post(path=url,data=data,content_type='application/json')
    assert response.status_code==400


@pytest.mark.django_db
def test_user_register_invalid_email(client):

    data={
        "username":"Tuddbnberuryggj",
        "email":"tuksdfccbnbmjkrgmail.com",
        "password":"tukavjjbmdsafs"

    }

    url=reverse('register')
    response=client.post(path=url,data=data,content_type='application/json')

    assert response.status_code==400


@pytest.mark.django_db
def test_user_register_invalid_password(client):

    data={
        "username":"Tuddbnberuryggj",
        "email":"tuksdfccbnbmjkr@gmail.com",
        "password":"tukavjj"
    }


    url=reverse('register')
    response=client.post(path=url,data=data,content_type='application/json')

    assert response.status_code==400


#login test scinarios
@pytest.mark.django_db
def test_user_login_api_success(client):

    data={
        "email":"tuksdfccvcnfehefhekr@gmail.com",
        "password":"tukavjjbmbvvbnv"
    }

    url=reverse('login')
    response=client.post(path=url,data=data,content_type='application/json')

    assert response.status_code==400

@pytest.mark.django_db
def test_user_login_api_invalid_creadential(client):
    
    data={
        "email":"tuksdfccbnbmjkr@gmail.com",
        "password":"tukavjjsf"

    }

    url=reverse('login')
    response=client.post(path=url,data=data,content_type='application/json')
    assert response.status_code==400


@pytest.mark.django_db
def test_login_user_missing_field(client):

    data={
         "email":"tuksdfccvcnfehefhekr@gmail.com",

    }

    url=reverse('login')
    response=client.post(path=url,data=data,content_type='application/json')
    assert response.status_code==400


@pytest.mark.django_db
def test_missing_login_all_fields(client):

    data={

    }

    url=reverse('login')
    response=client.post(path=url,data=data,content_type='application/json')

    assert response.status_code==400


# @pytest.mark.django_db
# def test_verify_registered_user_valid_token(client):
    
#     user = Users.objects.create_user(
#         email='bdamdfbat2659@gmail.com',
#         password='vsadvmasnvfsv',
#         username='Txababnbambcm'
#     )
#     token = RefreshToken.for_user(user).access_token
#     encoded_token = str(token)
#     url = reverse('verify', args=[encoded_token])
#     response = client.get(path=url)
#     assert response.status_code == 200
   

@pytest.mark.django_db
def test_verify_registered_user_invalid_token(client):

    invalid_token = "invalid.token.value"
    url = reverse('verify', args=[invalid_token])
    response = client.get(url)
    assert response.status_code == 400
    assert response.data['message'] == 'Invalid token'










