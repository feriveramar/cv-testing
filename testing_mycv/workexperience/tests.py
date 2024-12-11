from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link
from workexperience.models import WorkExperience
from workexperience.schema import schema
# Create your tests here.

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

CREATE_WORKEXPERIENCE_MUTATION = '''
mutation MyMutation ($idWorkExperience : Int!, $company: String!, $location: String!, $description: String!, $endDate: Date!, $startDate: Date!, $position: String!, $achievements: [String!]!) {
  createWorkexperience(idWorkExperience: $idWorkExperience, company:$company, location:$location, description:$description, endDate:$endDate, startDate:$startDate, position:$position, achievements:$achievements) {
    company
    description
    endDate
    position
    location
    idWorkExperience
    startDate
    achievements
}
}
'''

WORKEXPERIENCE_BY_ID_QUERY = '''
query positionById($idWorkExperience: Int!) {
  positionById(idWorkExperience: $idWorkExperience) {
    company
    description
    endDate
    position
    location
    startDate
    achievements
    id
    postedBy
    {
    username
    password
    }
  }
}
'''

WORKEXPERIENCE_NOQUERY = '''
{
  positions(search: "") {
    company
    description
    endDate
    position
    location
    achievements
    id
    startDate
    postedBy
    {
    username
    password
    }
  }
}
'''

WORKEXPERIENCE_QUERY = '''
{
  positions(search: "*") {
    company
    description
    endDate
    position
    location
    achievements
    id
    startDate
    postedBy
    {
    username
    password
    }
  }
}
'''

DELETE_WORKEXPERIENCE_MUTATION = '''
mutation DeleteWorkExperienceMutation($idWorkExperience: Int!) {
  deleteWorkexperience(idWorkExperience: $idWorkExperience) {
    idWorkExperience
  }
}
'''

class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        self.link1 = WorkExperience.objects.create(
        id=1, position= "Clerk", location= "Mexico", description= "xd", startDate= "2024-01-01", endDate="2024-02-02", achievements=["a", "b", "c"] 
        )
        self.link2 = WorkExperience.objects.create(
        id=2, position= "Clerk", location= "Mexico", description= "xd", startDate= "2024-01-01", endDate="2024-02-02", achievements=["a", "b", "c"] 
    )
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

    def test_createWorkExperience_mutation(self):
        response = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={'idWorkExperience': 1, 
                       'company':'UV',
                       'position': 'Clerk', 
                       'location': 'Mexico', 
                       'description': 'xd',
                        'startDate':'2024-01-01', 
                        'endDate':'2024-02-02',
                        'achievements': [
                            'a', 'b', 'c'
                        ]
                        },
                    headers=self.headers
            
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createWorkexperience": {'idWorkExperience': 1,'company':'UV', 'position': 'Clerk', 'location': 'Mexico', 'description': 'xd', 'startDate':'2024-01-01', 'endDate':'2024-02-02', 'achievements': ['a', 'b', 'c']}}, content['data'])
    
    def test_create_WorkExperience_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={'idWorkExperience': 1, 
                       'company':'UV',
                       'position': 'Clerk', 
                       'location': 'Mexico', 
                       'description': 'xd',
                        'startDate':'2024-01-01', 
                        'endDate':'2024-02-02',
                        'achievements': [
                            'a', 'b', 'c'
                        ]
                        }
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in !")
        self.assertTrue(WorkExperience.objects.filter(id=1).exists())

    def test_workexperience_NOquery(self):
        response = self.query(
            WORKEXPERIENCE_NOQUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['positions']),0)

    def test_workexperience_query(self):
        response = self.query(
            WORKEXPERIENCE_QUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['positions']),0)

    def test_query_workexperience_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            WORKEXPERIENCE_QUERY
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(WorkExperience.objects.filter(id=1).exists())
    
    def test_delete_WorkExperience_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            DELETE_WORKEXPERIENCE_MUTATION,
            variables={"idWorkExperience": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(WorkExperience.objects.filter(id=1).exists())

    def test_delete_workexperience_invalid_id(self):
        # Attempt to delete a non-existent position
        response = self.query(
            DELETE_WORKEXPERIENCE_MUTATION,
            variables={"idWorkExperience": 999},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Invalid WorkExperience id")

    def test_delete_WORKEXPERIENCE_success(self):
        # Successfully delete an existing position
        response = self.query(
            DELETE_WORKEXPERIENCE_MUTATION,
            variables={"idWorkExperience": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['deleteWorkexperience']['idWorkExperience'], 1)
        self.assertFalse(WorkExperience.objects.filter(id=1).exists())
    
    def test_position_by_id_not_logged_in(self):

        response = self.query(
            WORKEXPERIENCE_BY_ID_QUERY,
            variables={"idWorkExperience": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")

    def test_position_by_id_exists(self):

        response = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={'idWorkExperience': 1, 
                       'company':'UV',
                       'position': 'Clerk', 
                       'location': 'Mexico', 
                       'description': 'xd',
                        'startDate':'2024-01-01', 
                        'endDate':'2024-02-02',
                        'achievements': [
                            'a', 'b', 'c'    
                        ]
                        },
            headers=self.headers
        )
        content = json.loads(response.content)

        response = self.query(
            WORKEXPERIENCE_BY_ID_QUERY,
            variables={"idWorkExperience": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['positionById']['position'], "Clerk")

    def test_certificate_by_id_not_exists_or_not_owned(self):
        response = self.query(
            WORKEXPERIENCE_BY_ID_QUERY,
            variables={"idWorkExperience": 2},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(content['data']['positionById'])
