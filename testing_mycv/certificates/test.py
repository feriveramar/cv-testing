"""
WORKEXPERIENCE_BY_ID_QUERY = '''
            query GetExperienceById($id_experience: Int!) {
                experienceById(idWorkExperience: $id_experience) {
                    id
                    role
                }
            }
'''
from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from workexperience.schema import schema
from workexperience.models import WorkExperience

# Create your tests here.

WORKEXPERIENCE_QUERY = '''
query GetExperiences($search: String) {
  experiences(search: $search) {
    id
    role
  }
}
'''

WORKEXPERIENCE_BY_ID_QUERY = '''
            query GetExperienceById($id_experience: Int!) {
                experienceById(idWorkExperience: $id_experience) {
                    id
                    role
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
 mutation createWorkExperienceMutation($id_experience: Int!, $role: String!,
    $company: String!,
    $accomplishments: [String!]!,
    $start_date: Date!,
    $end_date: Date!,
    $location: String!) {
     createWorkExperience(idWorkExperience: $id_experience, role: $role,
        company: $company,
        accomplishments: $accomplishments,
        startDate: $start_date,
        endDate: $end_date,
        location: $location) {
         idWorkExperience
         role
     }
 }
'''

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

DELETE_WORKEXPERIENCE_MUTATION = '''
mutation DeleteWorkExperience($id_experience: Int!) {
    deleteWorkExperience(idWorkExperience: $id_experience) {
        idWorkExperience
    }
}
'''


class ExperienceTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.experience1 = mixer.blend(WorkExperience)
        self.experience2 = mixer.blend(WorkExperience)
   
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


    def test_experience_query(self):
        response = self.query(
            WORKEXPERIENCE_QUERY,
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
        assert len(content['data']['experiences']) == 0


    def test_users_query(self):
        response = self.query(
            USERS_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        print ("query users results ")
        print (response)
        assert len(content['data']['users']) == 3


    def test_createWorkExperience_mutation(self):
        response = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                'id_experience': 0,
                'role': 'Backend Engineer',
                'company': 'Code Factory',
                'accomplishments': [    ],
                'start_date': '2018-06-01',
                'end_date': '2020-12-31',
                'location': 'On-site'},
            headers=self.headers
        )
        content = json.loads(response.content)
        print("Response content:", content)
        created_experience_id = content['data']['createWorkExperience']['idWorkExperience']
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createWorkExperience": {"idWorkExperience": created_experience_id, "role": "Backend Engineer"}}, content['data']) 
        
    def test_experience_by_id_query(self):
        response_create = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                'id_experience': 0,
                'role': 'Backend Engineer',
                'company': 'Code Factory',
                'accomplishments': ['Built microservices', 'Optimized database queries'],
                'start_date': '2018-06-01',
                'end_date': '2020-12-31',
                'location': 'On-site'},
            headers=self.headers
        )
        
        content_create = json.loads(response_create.content)
        print("bbbbbbbbbbb:", content_create)
        created_experience_id = content_create['data']['createWorkExperience']['idWorkExperience']

        response = self.query(
          WORKEXPERIENCE_BY_ID_QUERY,
          variables={'id_experience': created_experience_id},
          headers=self.headers
        )
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['experienceById']['role'], "Backend Engineer")
        
    def test_update_existing_experience(self):
        response_create = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                'id_experience': 0,
                'role': 'Backend Engineer',
                'company': 'Code Factory',
                'accomplishments': ['Built microservices', 'Optimized database queries'],
                'start_date': '2018-06-01',
                'end_date': '2020-12-31',
                'location': 'On-site'},
            headers=self.headers
        )
        
        content_create = json.loads(response_create.content)
        created_experience_id = content_create['data']['createWorkExperience']['idWorkExperience']

        
        self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                'id_experience': created_experience_id,
                'role': 'Frontend Engineer',
                'company': 'Code Factory',
                'accomplishments': ['Built microservices', 'Optimized database queries'],
                'start_date': '2018-06-01',
                'end_date': '2020-12-31',
                'location': 'On-site'},
            headers=self.headers
        )

        response_query = self.query(
        WORKEXPERIENCE_BY_ID_QUERY,
        variables={'id_experience': created_experience_id},
        headers=self.headers
        )
        
        content_query = json.loads(response_query.content)
                
        
        response_query_all = self.query(
            WORKEXPERIENCE_QUERY,
             variables={
                'search': '*'},
            headers=self.headers
        )
        
        content = json.loads(response_query_all.content)

        assert len(content['data']['experiences']) == 1
        self.assertEqual(content_query['data']['experienceById']['role'], "Frontend Engineer")
        
    def test_not_logged_in(self):
        response = self.query(
            WORKEXPERIENCE_BY_ID_QUERY,
            variables={"id_experience": 1}
        )

        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Not logged in", content['errors'][0]['message'])

        response = self.query(
            WORKEXPERIENCE_QUERY,
            variables={"search": "*"}
        )
        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Not logged in!", content['errors'][0]['message'])

    def test_filter_search(self):
        self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                'id_experience': 1,
                'role': 'Backend Engineer',
                'company': 'Tech Solutions',
                'accomplishments': ['Developed APIs', 'Database optimization'],
                'start_date': '2019-01-01',
                'end_date': '2021-01-01',
                'location': 'Remote'
            },
            headers=self.headers
        )
        self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                'id_experience': 2,
                'role': 'Frontend Engineer',
                'company': 'Tech Solutions',
                'accomplishments': ['UI development', 'Testing'],
                'start_date': '2019-01-01',
                'end_date': '2021-01-01',
                'location': 'On-site'
            },
            headers=self.headers
        )

        response = self.query(
            WORKEXPERIENCE_QUERY,
            variables={"search": "Backend"},
            headers=self.headers
        )
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['experiences']), 1)
        self.assertEqual(content['data']['experiences'][0]['role'], "Backend Engineer")

        response = self.query(
            WORKEXPERIENCE_QUERY,
            variables={"search": "*"},
            headers=self.headers
        )
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(len(content['data']['experiences']), 2)

    def test_create_experience_not_logged_in(self):
        response = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                "id_experience": 0,
                "role": "Project Manager",
                "company": "Tech Corp",
                "accomplishments": ["Team leadership", "Strategic planning"],
                "start_date": "2017-01-01",
                "end_date": "2020-01-01",
                "location": "On-site"
            }
        )
        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Not logged in !", content['errors'][0]['message'])

    def test_delete_not_logged_in(self):
        self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                "id_experience": 1,
                "role": "Backend Engineer",
                "company": "Tech Solutions",
                "accomplishments": ["Developed APIs", "Database optimization"],
                "start_date": "2019-01-01",
                "end_date": "2021-01-01",
                "location": "Remote"
            },
            headers=self.headers
        )

        response = self.query(
            DELETE_WORKEXPERIENCE_MUTATION,
            variables={"id_experience": 1}
        )
        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Not logged in!", content['errors'][0]['message'])

    def test_invalid_experience_id(self):
        response = self.query(
            DELETE_WORKEXPERIENCE_MUTATION,
            variables={"id_experience": 9999},
            headers=self.headers
        )
        content = json.loads(response.content)

        self.assertIn('errors', content)
        self.assertIn("Invalid Work Experience id!", content['errors'][0]['message'])

    def test_delete_experience_successfully(self):
        response_create = self.query(
            CREATE_WORKEXPERIENCE_MUTATION,
            variables={
                "id_experience": 0,
                "role": "Software Developer",
                "company": "Innovate Inc.",
                "accomplishments": ["System architecture", "Code review"],
                "start_date": "2015-06-01",
                "end_date": "2018-06-01",
                "location": "Remote"
            },
            headers=self.headers
        )
        content_create = json.loads(response_create.content)
        created_experience_id = content_create['data']['createWorkExperience']['idWorkExperience']

        response = self.query(
            DELETE_WORKEXPERIENCE_MUTATION,
            variables={"id_experience": created_experience_id},
            headers=self.headers
        )
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['deleteWorkExperience']['idWorkExperience'], created_experience_id)

        experience_exists = WorkExperience.objects.filter(id=created_experience_id).exists()
        self.assertFalse(experience_exists)
"""