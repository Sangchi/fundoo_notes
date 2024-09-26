import pytest
from rest_framework.reverse import reverse
from rest_framework import status
import json
from user.models import Users
from loguru import logger
@pytest.fixture
def create_user(client):
   
    data = {
        "username":"Tagsjsdvdhv",
        "email": "sushenvnvnn@gmail.com",
        "password": "sushen1bmvmv234"
    }
    url = reverse('register')  
    response = client.post(url, data=data, content_type='application/json')
    
    assert response.status_code == status.HTTP_201_CREATED, f"User creation failed: {response.data}"
    return data

@pytest.fixture
def create_user_two(client):
 
    data = {
        "username":"Dhdbfbdbbcn",
        "email": "prashhvnvvn@gmail.com",
        "password": "prashantcncn"
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

@pytest.fixture
def generate_usertoken_two(client, create_user_two):

    data = {
        "email": create_user_two['email'],
        "password": create_user_two['password']
    }
    url = reverse('login') 
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.data}"
    return response.data["access"]

@pytest.mark.django_db
@pytest.mark.note
class TestNoteSuccess:

    NOTE_DATA = {
        "title": "Meeting",
        "description": "This is the description of my secret note.",
        "color": "violet",
        "is_archive": False,
        "is_trash": False,
        "reminder": "2024-08-26T11:50"
    }
    
    # Test: the create note 
    def test_note_create(self, client, generate_usertoken):

        url = reverse('note-list')  
        response = client.post(
            url,
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',
            data=self.NOTE_DATA,
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['title'] == self.NOTE_DATA['title']
        assert response.data['data']['description'] == self.NOTE_DATA['description']
        return response.data['data']['id']
        
    #Test: create note two
    def test_note_create_by_2user(self, client, generate_usertoken_two):

        url = reverse('note-list')  
        response = client.post(
            url,
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken_two}',
            data=self.NOTE_DATA,
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['title'] == self.NOTE_DATA['title']
        assert response.data['data']['description'] == self.NOTE_DATA['description']
        
        

    # Test: list all note of user
    def test_list_all_note_created_by_user_one(self,client,generate_usertoken):

        url=reverse('note-list')
        response=client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',
            content_type='application/json')
        
        assert response.status_code==status.HTTP_200_OK

    

     # Test: archive note
    def test_is_archive_note_user_one(self, client, generate_usertoken):

        note_id = self.test_note_create(client, generate_usertoken)
        url = reverse('note-archive', args=[note_id])
    
        self.NOTE_DATA['is_archive'] =not self.NOTE_DATA['is_archive']
    
        response = client.patch(
             url,
             data=self.NOTE_DATA,
             HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',
             content_type="application/json"
    )

        assert response.status_code == status.HTTP_200_OK

    #Test : archived note
    def test_archived_notes(self, client, generate_usertoken):

        url = reverse('note-is-archived')
        response = client.get(
            url, 
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', 
            content_type='application/json'
            
            )
        
        assert response.status_code == status.HTTP_200_OK
    
    # Test: trash note
    @pytest.mark.abc
    def test_is_trash_user_one(self, client, generate_usertoken):
        
        note_id = self.test_note_create(client, generate_usertoken)
        url = reverse('note-trash', args=[note_id])


        response = client.patch(
             path=url,
             HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', 
             content_type='application/json'
             )
        print(response.data)
    
        assert response.status_code == status.HTTP_200_OK
        


    #Test:Trashed note
    def test_trashed_notes(self, client, generate_usertoken):

        url = reverse('note-is-trashed')
        response = client.get(
            path=url,
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',
            content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK

    def test_update_note(self,client,generate_usertoken):
        
        note_id = self.test_note_create(client,generate_usertoken)
        data = {
        "title": "Meeting",
        "description": "Updated description",
        "reminder": "2024-08-26T11:50"
           }
        url = reverse('note-detail', args=[note_id])
        response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        
        assert response.status_code == status.HTTP_200_OK
        

    #test : add collbarator
    def test_add_collaborators(self, client, generate_usertoken, generate_usertoken_two):
   
        note_id = self.test_note_create(client, generate_usertoken)
        collaborator_user_id = Users.objects.get(email="prashhvnvvn@gmail.com").id
        
  
        data = {
            "note_id": note_id,
            "user_ids": [collaborator_user_id]
        }
        
        url = reverse('note-add-collaborators')
        response = client.post(
            url,
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "Collaborators added successfully" in response.data['message']

    #Test : remove collabrator
    def test_remove_collaborators(self, client, generate_usertoken, generate_usertoken_two):

        note_id = self.test_note_create(client, generate_usertoken)
        collaborator_res = Users.objects.get(email="prashhvnvvn@gmail.com").id
      
    
        self.test_add_collaborators(client, generate_usertoken, generate_usertoken_two)

        data = {
        "note_id": note_id,
        "user_ids": [collaborator_res] 
          }
    
        url = reverse('note-remove-collaborators')
    
        response = client.post(
             url,
             data=data,
             HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', 
             content_type='application/json'
                 )
    
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Test: Add labels to a note
    def test_add_labels(self, client, generate_usertoken):

        note_id = self.test_note_create(client, generate_usertoken)
      
        data = {
            "note_id": note_id,
            "label_ids": [1, 2]
        }
        url = reverse('note-add-labels')
        response = client.post(
            url, 
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', 
            data=data, 
            content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert "Labels added successfully" in response.data['message']


    # Test: Remove labels from a note
    def test_remove_labels(self, client, generate_usertoken):

        note_id = self.test_note_create(client, generate_usertoken)
        
        self.test_add_labels(client, generate_usertoken)
        data = {
            "note_id": note_id,
            "label_ids": [1, 2]
        }
        url = reverse('note-remove-labels')
        response = client.post(
            url,
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', 
            data=data, 
            content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert "Labels removed successfully" in response.data['message']


    # Test: Delete a note
    def test_delete_note(self, client, generate_usertoken):

        note_id = self.test_note_create(client, generate_usertoken)
        logger.info(note_id)
        url = reverse('note-detail', args=[note_id])
        response = client.delete(
            url, 
            HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', 
            content_type='application/json')
        assert response.status_code == status.HTTP_204_NO_CONTENT


    # Test: Invalid data when creating a note
    def test_note_create_invalid_data(self, client, generate_usertoken):

        data = {
            "title": "", 
            "description": "Missing title test.",
            "reminder": "2024-08-26T11:50"
        }
        url = reverse('note-list')
        response = client.post(
            url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    

    # Test: Create a note with a missing required field
    def test_note_create_missing_field(self, client, generate_usertoken):

        data = {
            "description": "Missing title test.",
            "reminder": "2024-08-26T11:50"
        }
        url = reverse('note-list')
        response = client.post(
            url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
     

    # Test: Attempt to list notes without authentication
    def test_note_list_unauthenticated(self, client):

        url = reverse('note-list')
        response = client.get(
            url, content_type='application/json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test: Ensure note cannot be fetched with invalid ID
    def test_note_fetch_invalid_id(self, client, generate_usertoken):
    
        url = reverse('note-detail', args=[9999])
        response = client.get(
            url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', content_type='application/json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # Test: Ensure reminder date validation
    def test_note_create_invalid_reminder_date(self, client, generate_usertoken):

        data = {
            "title": "Reminder",
            "description": "Invalid reminder date",
            "reminder": "invalid-date"
        }
        url = reverse('note-list')
        response = client.post(
            url, HTTP_AUTHORIZATION=f'Bearer {generate_usertoken}', data=data, content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
