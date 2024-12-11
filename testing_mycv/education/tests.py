from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link
from education.models import Education
from education.schema import schema

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

EDUCATION_NOQUERY = '''
{
  degrees(search: "") {
    degree
    endDate
    id
    startDate
    university
    postedBy
    {
    username
    password
    }
  }
}
'''

EDUCATION_QUERY = '''
{
  degrees(search: "*") {
    degree
    endDate
    id
    startDate
    university
    postedBy
    {
    username
    password
    }
  }
}
'''

EDUCATION_BY_ID_QUERY = '''
query degreeById($idEducation: Int!) {
  degreeById(idEducation: $idEducation) {
    degree
    endDate
    id
    startDate
    university
  }
}
'''

DELETE_EDUCATION_MUTATION = '''
mutation deleteEducation($idEducation: Int!) {
  deleteEducation(idEducation: $idEducation) {
    idEducation
  }
}
'''

CREATE_EDUCATION_MUTATION = '''
mutation MyMutation ($idEducation : Int!, $degree: String! , $university: String!, $startDate: Date! $endDate: Date!) {
  createEducation(idEducation: $idEducation, degree: $degree, startDate:$startDate, university: $university, endDate:$endDate ) {
    degree
    endDate
    idEducation
    startDate
    university
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
class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        
        self.link1= Education.objects.create(
            id=1, degree= "UV", endDate= "2024-02-02", startDate="2023-03-01", university= "UV"
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

    def test_create_Skills_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            CREATE_EDUCATION_MUTATION,
            variables={'idEducation': 1, 'degree': 'UV', 'startDate': '2024-02-01' , 'endDate': "2024-09-02", 'university': 'Google'}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in !")
        self.assertTrue(Education.objects.filter(id=1).exists())

    def test_createEducation_mutation(self):
        response = self.query(
            CREATE_EDUCATION_MUTATION,
            variables={'idEducation': 1, 'degree': 'UV', 'startDate': '2024-02-01' , 'endDate': "2024-09-02", 'university': 'Google'},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createEducation": {'idEducation': 1, 'degree': 'UV', 'startDate': '2024-02-01' , 'endDate': "2024-09-02", 'university': 'Google'}}, content['data'])

    def test_delete_Education_success(self):
        # Successfully delete an existing certificate
        response = self.query(
            DELETE_EDUCATION_MUTATION,
            variables={"idEducation": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['deleteEducation']['idEducation'], 1)
        self.assertFalse(Education.objects.filter(id=1).exists())  # Certificate should be deleted

    def test_delete_certificates_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            DELETE_EDUCATION_MUTATION,
            variables={"idEducation": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Education.objects.filter(id=1).exists())  # Certificate should still exist
    
    def test_delete_certificates_invalid_id(self):
        # Attempt to delete a non-existent certificate
        response = self.query(
            DELETE_EDUCATION_MUTATION,
            variables={"idEducation": 999},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Invalid Education id")

    def test_Educations_NOquery(self):
        response = self.query(
            EDUCATION_NOQUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['degrees']),0)

    def test_Educations_query(self):
        response = self.query(
            EDUCATION_QUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['degrees']),0)
    
    def test_query_Education_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            EDUCATION_NOQUERY
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Education.objects.filter(id=1).exists())

    def test_education_by_id_exists(self):

        response = self.query(
            CREATE_EDUCATION_MUTATION,
            variables={'idEducation': 1, 'degree': 'UV', 'startDate': '2024-02-01' , 'endDate': "2024-09-02", 'university': 'Google'},
            headers=self.headers
        )
        content = json.loads(response.content)

        response = self.query(
            EDUCATION_BY_ID_QUERY,
            variables={"idEducation": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['degreeById']['degree'], "UV")

    def test_education_by_id_not_exists_or_not_owned(self):
        response = self.query(
            EDUCATION_BY_ID_QUERY,
            variables={"idEducation": 2},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(content['data']['degreeById'])
    
    def test_skill_by_id_not_logged_in(self):

        response = self.query(
            EDUCATION_BY_ID_QUERY,
            variables={"idEducation": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")