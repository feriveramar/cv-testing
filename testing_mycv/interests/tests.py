from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link
from interests.models import Interests
from interests.schema import schema

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

CREATE_INTERESTS_MUTATION = '''
mutation MyMutation ($idInterests : Int!, $name: String!) {
  createInterests(idInterests: $idInterests, name: $name) {
    idInterests
    name
}
}
'''

INTERESTS_BY_ID_QUERY = '''
query interestById($idInterests: Int!) {
  interestById(idInterests: $idInterests) {
    id
    name
  }
}
'''

INTERESTS_NOQUERY = '''
{
  interests(search: "") {
    id
    name
    postedBy
    {
    username
    password
    }
  }
}
'''

INTERESTS_QUERY = '''
{
  interests(search: "*") {
    id
    name
    postedBy
    {
    username
    password
    }
  }
}
'''

DELETE_INTERESTS_MUTATION = '''
mutation DeleteInterestsMutation($idInterests: Int!) {
  deleteInterests(idInterests: $idInterests) {
    idInterests
  }
}
'''

class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        self.link1 = Interests.objects.create(
        id=1, name="Language Learning"
        )
        self.link2 = Interests.objects.create(
        id=2, name="Hacking"
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

    def test_createInterest_mutation(self):
        response = self.query(
            CREATE_INTERESTS_MUTATION,
            variables={'idInterests': 1, 'name': 'UV'},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createInterests": {'idInterests': 1, 'name': 'UV'}}, content['data'])
    
    def test_create_Interests_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            CREATE_INTERESTS_MUTATION,
            variables={'idInterests': 1, 'name': 'UV'}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in !")
        self.assertTrue(Interests.objects.filter(id=1).exists())

    def test_interests_NOquery(self):
        response = self.query(
            INTERESTS_NOQUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['interests']),0)

    def test_interests_query(self):
        response = self.query(
            INTERESTS_QUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['interests']),0)

    def test_query_interests_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            INTERESTS_QUERY
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Interests.objects.filter(id=1).exists())
    
    def test_delete_Interests_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            DELETE_INTERESTS_MUTATION,
            variables={"idInterests": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Interests.objects.filter(id=1).exists())

    def test_delete_interests_invalid_id(self):
        # Attempt to delete a non-existent interest
        response = self.query(
            DELETE_INTERESTS_MUTATION,
            variables={"idInterests": 999},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Invalid Interests id")

    def test_delete_INTERESTs_success(self):
        # Successfully delete an existing interest
        response = self.query(
            DELETE_INTERESTS_MUTATION,
            variables={"idInterests": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['deleteInterests']['idInterests'], 1)
        self.assertFalse(Interests.objects.filter(id=1).exists())
    
    def test_interest_by_id_not_logged_in(self):

        response = self.query(
            INTERESTS_BY_ID_QUERY,
            variables={"idInterests": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")

    def test_interest_by_id_exists(self):

        response = self.query(
            CREATE_INTERESTS_MUTATION,
            variables={'idInterests': 1, 'name': 'UV'},
            headers=self.headers
        )
        content = json.loads(response.content)

        response = self.query(
            INTERESTS_BY_ID_QUERY,
            variables={"idInterests": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['interestById']['name'], "UV")

    def test_certificate_by_id_not_exists_or_not_owned(self):
        response = self.query(
            INTERESTS_BY_ID_QUERY,
            variables={"idInterests": 2},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(content['data']['interestById'])
