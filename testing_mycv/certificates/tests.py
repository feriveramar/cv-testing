from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link
from certificates.models import Certificates
from certificates.schema import schema


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

CERTIFICATES_QUERY = '''
{
  certificates(search: "*") {
    id
    institution
    title
    year
    postedBy
    {
    username
    password
    }
  }
}
'''

CERTIFICATES_NOQUERY = '''
{
  certificates(search: "") {
    id
    institution
    title
    year
    postedBy
    {
    username
    password
    }
  }
}
'''

CREATE_CERTIFICATES_MUTATION = '''
mutation MyMutation ($idCertificates : Int!, $institution: String!, $year: Int! , $title: String!) {
  createCertificates(idCertificates: $idCertificates, institution: $institution, year:$year, title: $title) {
    idCertificates
    institution
    year
}
}
'''

DELETE_CERTIFICATES_MUTATION = '''
mutation DeleteCertificatesMutation($idCertificates: Int!) {
  deleteCertificates(idCertificates: $idCertificates) {
    idCertificates
  }
}
'''

CERTIFICATE_BY_ID_QUERY = '''
query CertificateById($idCertificates: Int!) {
  certificateById(idCertificates: $idCertificates) {
    id
    title
    institution
    year
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
        
        self.link1 = Certificates.objects.create(
        id=1, institution="Google", year=2024, title="UV"
        )
        self.link2 = Certificates.objects.create(
        id=2, institution="Microsoft", year=2023, title="Azure"
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

    def test_createCertificate_mutation(self):
        response = self.query(
            CREATE_CERTIFICATES_MUTATION,
            variables={'idCertificates': 1, 'title': 'UV', 'year': 2024, 'institution': 'Google'},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createCertificates": {'idCertificates': 1,'year': 2024, 'institution': 'Google'}}, content['data'])

    def test_create_certificates_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            CREATE_CERTIFICATES_MUTATION,
            variables={'idCertificates': 1, 'title': 'UV', 'year': 2024, 'institution': 'Google'}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in !")
        self.assertTrue(Certificates.objects.filter(id=1).exists())
    
    def test_links_query(self):
        response = self.query(
            CERTIFICATES_NOQUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['certificates']),0)
        

    def test_query_certificates_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            CERTIFICATES_QUERY
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Certificates.objects.filter(id=1).exists())

    def test_delete_certificates_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            DELETE_CERTIFICATES_MUTATION,
            variables={"idCertificates": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Certificates.objects.filter(id=1).exists())  # Certificate should still exist

    def test_delete_certificates_invalid_id(self):
        # Attempt to delete a non-existent certificate
        response = self.query(
            DELETE_CERTIFICATES_MUTATION,
            variables={"idCertificates": 999},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Invalid Certificates id")

    def test_delete_certificates_success(self):
        # Successfully delete an existing certificate
        response = self.query(
            DELETE_CERTIFICATES_MUTATION,
            variables={"idCertificates": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['deleteCertificates']['idCertificates'], 1)
        self.assertFalse(Certificates.objects.filter(id=1).exists())  # Certificate should be deleted

    def test_certificate_by_id_not_logged_in(self):

        response = self.query(
            CERTIFICATE_BY_ID_QUERY,
            variables={"idCertificates": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")

    def test_certificate_by_id_exists(self):

        response = self.query(
            CREATE_CERTIFICATES_MUTATION,
            variables={'idCertificates': 1, 'title': 'UV', 'year': 2024, 'institution': 'Google'},
            headers=self.headers
        )
        content = json.loads(response.content)

        response = self.query(
            CERTIFICATE_BY_ID_QUERY,
            variables={"idCertificates": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['certificateById']['title'], "UV")

    def test_certificates_exists(self):

        response = self.query(
            CREATE_CERTIFICATES_MUTATION,
            variables={'idCertificates': 1, 'title': 'UV', 'year': 2024, 'institution': 'Google'},
            headers=self.headers
        )
        content = json.loads(response.content)
        response = self.query(
            CERTIFICATES_QUERY,
            variables={
                'search': '*'},
            headers=self.headers
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        print ("query experiences results ")
        print (response)
        self.assertEqual(content['data']['certificates'][0]['title'], "UV")
        self.assertEqual(len(content['data']['certificates']), 1)

    def test_certificate_by_id_not_exists_or_not_owned(self):
        response = self.query(
            CERTIFICATE_BY_ID_QUERY,
            variables={"idCertificates": 2},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(content['data']['certificateById'])

    
        

