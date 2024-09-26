import pytest
from rest_framework.reverse import reverse
from rest_framework import status
from user.models import Users
from label.views import LabelViewSet

@pytest.fixture
def create_user(client):
    data = {
        "username": "Tagsjsdvdhv",
        "email": "sushenvnvnn@gmail.com",
        "password": "sushen1bmvmv234"
    }
    url = reverse('register')  
    response = client.post(url, data=data, content_type='application/json')
    
    assert response.status_code == status.HTTP_201_CREATED, f"User creation failed: {response.data}"
    return data

@pytest.fixture
def generate_usertoken(client, create_user):
    data = {
        "email": create_user['email'],
        "password": create_user['password']
    }
    url = reverse('login')  
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.data}"
    return response.data["access"]

@pytest.mark.django_db
@pytest.mark.note
class TestLabelSuccess:
    def test_create_labels(self, client, generate_usertoken):
        label_data = {
            "name": "the book",
            "color": "black"
        }
        
        url = reverse('label-list')  
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=label_data, content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        return response.data['data']['id']


    def test_create_labels_internal_server_fields_error(self, client, generate_usertoken):
        label_data = {"name": "",
            "color": "black"}
        
        url = reverse('label-list') 
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=label_data, content_type='application/json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


    def test_label_create_number_data(self, client, generate_usertoken):
        data = {
            "name": 123,
            "color": "Yellow"
        }
        url = reverse('label-list')  
        response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST  


    def test_label_create_unauthorized(self, client):
        data = {
            "name": "Ccshgcsc",
            "color": "Yellow"
        }
        url = reverse('label-list') 
        response = client.post(url, data=data, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_get_all_labels(self, client, generate_usertoken):
        url = reverse('label-list') 
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK

        

    def test_get_all_labels_unauthorized(self, client):
        url = reverse('label-list')
        response = client.get(url, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED



    def test_update_label(self, client, generate_usertoken):
        label_id = self.test_create_labels(client, generate_usertoken) 
        data = {
            "name": "Updated Book",
            "color": "Yellow"
        }
        url = reverse('label-detail', args=[label_id]) 
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_200_OK



    def test_update_label_invalid_(self, client, generate_usertoken):
        invalid_label_id = 9999
        data = {
            "name": "Non-existent Label",
            "color": "Yellow"
        }
        url = reverse('label-detail', args=[invalid_label_id]) 
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


    def test_update_label_unauthenticated(self, client):
        label_id = 1  
        data = {
            "name": "Unauthorized Update",
            "color": "Yellow"
        }
        url = reverse('label-detail', args=[label_id]) 
        response = client.put(url, data=data, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_destroy_label(self, client, generate_usertoken):
        label_id = self.test_create_labels(client, generate_usertoken)  
        url = reverse('label-detail', args=[label_id])  
        response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK


    def test_destroy_label_by_unauthorized_user(self, client):
        
        label_id = 456

        url = reverse('label-detail', args=[label_id]) 
        response = client.delete(url,  content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
