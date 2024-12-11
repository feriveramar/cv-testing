from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link
from skills.models import Skills
from skills.schema import schema

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

CREATE_SKILLS_MUTATION = '''
mutation MyMutation ($idSkills : Int!, $name: String!) {
  createSkills(idSkills: $idSkills, name: $name) {
    idSkills
    name
}
}
'''

SKILLS_BY_ID_QUERY = '''
query skillById($idSkills: Int!) {
  skillById(idSkills: $idSkills) {
    id
    name
  }
}
'''

SKILLS_NOQUERY = '''
{
  skills(search: "") {
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

SKILLS_QUERY = '''
{
  skills(search: "*") {
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

DELETE_SKILLS_MUTATION = '''
mutation DeleteSkillsMutation($idSkills: Int!) {
  deleteSkills(idSkills: $idSkills) {
    idSkills
  }
}
'''

class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        self.link1 = Skills.objects.create(
        id=1, name="Language Learning"
        )
        self.link2 = Skills.objects.create(
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

    def test_createSkill_mutation(self):
        response = self.query(
            CREATE_SKILLS_MUTATION,
            variables={'idSkills': 1, 'name': 'UV'},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createSkills": {'idSkills': 1, 'name': 'UV'}}, content['data'])
    
    def test_create_Skills_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            CREATE_SKILLS_MUTATION,
            variables={'idSkills': 1, 'name': 'UV'}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in !")
        self.assertTrue(Skills.objects.filter(id=1).exists())

    def test_skills_NOquery(self):
        response = self.query(
            SKILLS_NOQUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['skills']),0)

    def test_skills_query(self):
        response = self.query(
            SKILLS_QUERY,
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual (len(content['data']['skills']),0)

    def test_query_skills_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            SKILLS_QUERY
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Skills.objects.filter(id=1).exists())
    
    def test_delete_Skills_not_logged_in(self):
        # Attempt to delete without authentication
        response = self.query(
            DELETE_SKILLS_MUTATION,
            variables={"idSkills": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")
        self.assertTrue(Skills.objects.filter(id=1).exists())

    def test_delete_skills_invalid_id(self):
        # Attempt to delete a non-existent skill
        response = self.query(
            DELETE_SKILLS_MUTATION,
            variables={"idSkills": 999},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Invalid Skills id")

    def test_delete_SKILLs_success(self):
        # Successfully delete an existing skill
        response = self.query(
            DELETE_SKILLS_MUTATION,
            variables={"idSkills": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['deleteSkills']['idSkills'], 1)
        self.assertFalse(Skills.objects.filter(id=1).exists())
    
    def test_skill_by_id_not_logged_in(self):

        response = self.query(
            SKILLS_BY_ID_QUERY,
            variables={"idSkills": 1}
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn("errors", content)
        self.assertEqual(content['errors'][0]['message'], "Not logged in!")

    def test_skill_by_id_exists(self):

        response = self.query(
            CREATE_SKILLS_MUTATION,
            variables={'idSkills': 1, 'name': 'UV'},
            headers=self.headers
        )
        content = json.loads(response.content)

        response = self.query(
            SKILLS_BY_ID_QUERY,
            variables={"idSkills": 1},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("errors", content)
        self.assertEqual(content['data']['skillById']['name'], "UV")

    def test_certificate_by_id_not_exists_or_not_owned(self):
        response = self.query(
            SKILLS_BY_ID_QUERY,
            variables={"idSkills": 2},
            headers=self.headers
        )
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(content['data']['skillById'])



