from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
import json
from mixer.backend.django import mixer
from django.contrib.auth import get_user_model

from .models import Header
from header.schema import schema

# GraphQL Queries and Mutations


CREATE_USER_MUTATION = '''
 mutation createUserMutation($email: String!, $password: String!, $username: String!) {
     createUser(email: $email, password: $password, username: $username) {
         user {
            username
            password
         }
     }
 }
'''

LOGIN_USER_MUTATION = '''
 mutation TokenAuthMutation($username: String!, $password: String!) {
     tokenAuth(username: $username, password: $password) {
        token
     }
 }
'''

USERS_QUERY = '''
 {
   users {
     id
     username
     password
   }
 }
'''

CREATE_OR_UPDATE_HEADER_MUTATION = '''
mutation CreateOrUpdateHeader($title: String!, $description: String!, $phone: String!, $address:String!, $email:String!, $socialmedia:String!, $url:String!) {
  createOrUpdateHeader(title: $title, description: $description, phone:$phone, address:$address, email:$email, socialmedia:$socialmedia, url:$url) {
    idHeader
    title
    url
    description
    phone
    address
    email
    socialmedia
    postedBy {
      username
    }
  }
}
'''

GET_HEADER_QUERY = '''
query {
  header {
    url
    id
    title
    description
    phone
    address
    email
    socialmedia
    postedBy {
      username
    }
  }
}
'''

class HeaderTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        response_user = self.query(
            CREATE_USER_MUTATION,
            variables={'email': 'adsoft@live.com.mx', 'username': 'adsoft', 'password': 'adsoft'}
        )
        print('user mutation ')
        content_user = json.loads(response_user.content)
        print(content_user['data'])

        response_token = self.query(
            LOGIN_USER_MUTATION,
            variables={'username': 'adsoft', 'password': 'adsoft'}
        )

        content_token = json.loads(response_token.content)
        token = content_token['data']['tokenAuth']['token']
        print(token)
        self.headers = {"AUTHORIZATION": f"JWT {token}"}

        self.initial_title = "Initial Title"
        self.initial_description = "Initial Description"
        Header.objects.create(
            id=1,
            title=self.initial_title,
            description=self.initial_description
        )
        


    def test_get_header(self):
        new_title = "Updated Header Title"
        new_description = "Updated Header Description"
    
    # Perform the mutation to update or create the header
        response = self.query(
        CREATE_OR_UPDATE_HEADER_MUTATION,
        variables={"title": new_title, "description": new_description, "phone":"123456", "email": "orizaba@gmail.com", "address":"123", "socialmedia": "@sam", "url": "https://www.google.com/maps"},
        headers=self.headers
    )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createOrUpdateHeader']['title'], new_title)
        self.assertEqual(content['data']['createOrUpdateHeader']['description'], new_description)

    # Perform the query to retrieve the updated header
        response = self.query(
        GET_HEADER_QUERY,
        headers=self.headers
    )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['header']['title'], new_title)  # Use 'header' here
        self.assertEqual(content['data']['header']['description'], new_description)  # Use 'header' here


    def test_create_or_update_header(self):
        new_title = "Updated Header Title"
        new_description = "Updated Header Description"
        response = self.query(
            CREATE_OR_UPDATE_HEADER_MUTATION,
            variables={"title": new_title, "description": new_description, "phone":"123456", "email": "orizaba@gmail.com", "address":"123", "socialmedia": "@sam", "url": "https://www.google.com/maps"},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createOrUpdateHeader']['title'], new_title)
        self.assertEqual(content['data']['createOrUpdateHeader']['description'], new_description)

        # Check the database
        header = Header.objects.first()
        self.assertEqual(header.title, new_title)
        self.assertEqual(header.description, new_description)

    def test_create_or_update_header_not_logged_in(self):
        new_title = "Unauthorized Update"
        new_description = "This should fail"
        response = self.query(
            CREATE_OR_UPDATE_HEADER_MUTATION,
            variables={"title": new_title, "description": new_description, "phone":"123456", "email": "orizaba@gmail.com", "address":"123", "socialmedia": "@sam", "url": "https://www.google.com/maps"}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")

    def test_get_header_not_logged_in(self):
        response = self.query(GET_HEADER_QUERY)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")

    def test_header_creation_when_already_exists(self):
        # Attempt to create another header while one already exists
        new_title = "Second Header Attempt"
        new_description = "This should update the existing header"
        response = self.query(
            CREATE_OR_UPDATE_HEADER_MUTATION,
            variables={"title": new_title, "description": new_description, "phone":"123456", "email": "orizaba@gmail.com", "address":"123", "socialmedia": "@sam", "url": "https://www.google.com/maps"},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)

        # Check that the existing header was updated
        header = Header.objects.first()
        self.assertEqual(header.title, new_title)
        self.assertEqual(header.description, new_description)

    def test_header_absence_handling(self):
        # Delete the header and query for it
        Header.objects.all().delete()
        response = self.query(
            GET_HEADER_QUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Header not found!")
    
    def test_update_existing_header(self):
        # New data to update the existing Header
        updated_title = "Updated Title"
        updated_description = "Updated Description"

        # Perform the mutation
        response = self.query(
            CREATE_OR_UPDATE_HEADER_MUTATION,
            variables={
                "title": updated_title, "description": updated_description, "phone":"123456", "email": "orizaba@gmail.com", "address":"123", "socialmedia": "@sam", "url": "https://www.google.com/maps"
            },
            headers=self.headers
        )
        content = json.loads(response.content)

        # Assertions
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createOrUpdateHeader']['title'], updated_title)
        self.assertEqual(content['data']['createOrUpdateHeader']['description'], updated_description)
     
        # Verify the database changes
        header = Header.objects.get(id=1)
        self.assertEqual(header.title, updated_title)
        self.assertEqual(header.description, updated_description)
