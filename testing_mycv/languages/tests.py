from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link
from languages.models import Languages
from languages.schema import schema

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

CREATE_LANGUAGES_MUTATION = '''
mutation MyMutation ($idLanguages : Int!, $language: String!, $level: String!) {
  createLanguages(idLanguages: $idLanguages, language:$language, level:$level) {
    idLanguages
    language
    level
}
}
'''

LANGUAGES_BY_ID_QUERY = '''
query languageById($idLanguages: Int!) {
  languageById(idLanguages: $idLanguages) {
    id
    language
    level
  }
}
'''

LANGUAGES_NOQUERY = '''
{
  languages(search: "") {
    id
    language
    level
    postedBy
    {
    username
    password
    }
  }
}
'''

LANGUAGES_QUERY = '''
{
  languages(search: "*") {
    id
    language
    level
    postedBy
    {
    username
    password
    }
  }
}
'''

DELETE_LANGUAGES_MUTATION = '''
mutation DeleteLanguagesMutation($idLanguages: Int!) {
  deleteLanguages(idLanguages: $idLanguages) {
    idLanguages
  }
}
'''

class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        self.link1 = Languages.objects.create(
        id=1, language="English", level = "C1" 
        )
        self.link2 = Languages.objects.create(
        id=2, language="Spanish", level= "C2"
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

    def test_createLanguage_mutation(self):
        response = self.query(
            CREATE_LANGUAGES_MUTATION,
            variables={'idLanguages': 1, 'language': 'English', 'level': 'B2'},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createLanguages": {'idLanguages': 1, 'language': 'English', 'level':'B2'}}, content['data'])
    
    def test_create_Languages_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            CREATE_LANGUAGES_MUTATION,
            variables={'idLanguages': 1, 'language': 'English', 'level':'C2'}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in !")
        self.assertTrue(Languages.objects.filter(id=1).exists())

    def test_languages_NOquery(self):
        response = self.query(
            LANGUAGES_NOQUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['languages']),0)

    def test_languages_query(self):
        response = self.query(
            LANGUAGES_QUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['languages']),0)

    def test_query_languages_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            LANGUAGES_QUERY
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Languages.objects.filter(id=1).exists())
    
    def test_delete_Languages_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            DELETE_LANGUAGES_MUTATION,
            variables={"idLanguages": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Languages.objects.filter(id=1).exists())

    def test_delete_languages_invalid_id(self):
        # Attempt to delete a non-existent language
        response = self.query(
            DELETE_LANGUAGES_MUTATION,
            variables={"idLanguages": 999},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Invalid Language id")

    def test_delete_LANGUAGEs_success(self):
        # Successfully delete an existing language
        response = self.query(
            DELETE_LANGUAGES_MUTATION,
            variables={"idLanguages": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['deleteLanguages']['idLanguages'], 1)
        self.assertFalse(Languages.objects.filter(id=1).exists())
    
    def test_language_by_id_not_logged_in(self):

        response = self.query(
            LANGUAGES_BY_ID_QUERY,
            variables={"idLanguages": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")

    def test_language_by_id_exists(self):

        response = self.query(
            CREATE_LANGUAGES_MUTATION,
            variables={'idLanguages': 1, 'language': 'UV', 'level':'C2'},
            headers=self.headers
        )
        content = json.loads(response.content)

        response = self.query(
            LANGUAGES_BY_ID_QUERY,
            variables={"idLanguages": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['languageById']['language'], "UV")

    def test_certificate_by_id_not_exists_or_not_owned(self):
        response = self.query(
            LANGUAGES_BY_ID_QUERY,
            variables={"idLanguages": 2},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(content['data']['languageById'])



