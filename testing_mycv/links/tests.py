from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from mixer.backend.django import mixer
import graphene
import json
from django.contrib.auth import get_user_model

from links.schema import schema
from links.models import Link
from links.models import Vote

# Create your tests here.

LINKS_QUERY = '''
 {
   links {
     id
     url
     description
   }
 }
'''

VOTES_QUERY = '''
 {
                links {
                    description
                    id
                    url
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
CREATE_VOTE_MUTATION = '''
mutation createVoteMutation($linkId: Int!) {
                createVote(linkId: $linkId) {
                    link {
                        url
                        description
                        id
                    }
                }
            }
            '''



CREATE_LINK_MUTATION = '''
 mutation createLinkMutation($url: String, $description: String) {
     createLink(url: $url, description: $description) {
         description
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

class LinkTestCase(GraphQLTestCase):
    GRAPHQL_URL = "http://localhost:8000/graphql/"
    GRAPHQL_SCHEMA = schema
    
    def setUp(self):
        self.link1 = mixer.blend(Link)
        self.link2 = mixer.blend(Link)

        self.vote1 = mixer.blend(Vote, link=self.link1)
        self.vote2 = mixer.blend(Vote, link=self.link2)
        self.vote3 = mixer.blend(Vote, link=self.link1)

        print("Users after cleanup:", get_user_model().objects.count())

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


    def test_links_query(self):
        response = self.query(
            LINKS_QUERY,
        )
        print(response)
        content = json.loads(response.content)
        print(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)
        print ("query link results ")
        print (response)
        assert len(content['data']['links']) == 2

    def test_votes_query(self):
        # Query for all votes
        response = self.query(
            '''
            query MyQuery {
                votes {
                    id
                    link {
                        url
                        description
                    }
                }
            }
            '''
        )
        
        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        
        # Ensure the number of votes returned matches the number of votes created
        votes_data = content['data']['votes']
        assert len(votes_data) == 3  # We created 3 votes (2 on link1, 1 on link2)

        # Ensure that the vote data matches what's expected (i.e., link data)
        vote_ids = [vote['id'] for vote in votes_data]
        assert self.vote1.id == int(vote_ids[0]) or self.vote1.id == int(vote_ids[1])
        assert self.vote2.id == int(vote_ids[0]) or self.vote2.id == int(vote_ids[1])
        assert self.vote3.id == int(vote_ids[0]) or self.vote3.id == int(vote_ids[2])

        # Ensure that the links associated with the votes are correct
        link_urls = [vote['link']['url'] for vote in votes_data]
        assert self.link1.url in link_urls
        assert self.link2.url in link_urls

        link_descriptions = [vote['link']['description'] for vote in votes_data]
        assert self.link1.description in link_descriptions
        assert self.link2.description in link_descriptions


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


        assert len(content['data']['users']) == 6


    def test_createLink_mutation(self):
        response = self.query(
            CREATE_LINK_MUTATION,
            variables={'url': 'https://google.com', 'description': 'google'},
            headers=self.headers
        )
        content = json.loads(response.content)
        print(content['data'])
        self.assertResponseNoErrors(response)
        self.assertDictEqual({"createLink": {"description": "google"}}, content['data']) 

    def test_vote_as_anonymous_user(self):
        """Test that an anonymous user cannot vote."""
        response = self.query(
            CREATE_VOTE_MUTATION,
            variables={'linkId': self.link1.id}
        )
        content = json.loads(response.content)
        
        # Check that the error message is as expected
        self.assertResponseHasErrors(response)
        self.assertIn('GraphQLError: You must be logged to vote!', str(content['errors']))

    def test_vote_with_invalid_link(self):
        """Test that voting on an invalid link raises an error."""
        response = self.query(
            CREATE_VOTE_MUTATION,
            variables={'linkId': 9999},  # Invalid link ID
            headers=self.headers
        )
        content = json.loads(response.content)
        
        # Check that the error message is as expected
        self.assertResponseHasErrors(response)
        self.assertIn('Invalid Link!', str(content['errors']))

    def test_vote_on_link(self):
        # Vote on the first link (using its ID)
        response_vote = self.query(
            '''
            mutation createVoteMutation($linkId: Int!) {
                createVote(linkId: $linkId) {
                    link {
                        url
                        description
                        id
                    }
                }
            }
            ''',
            variables={'linkId': self.link1.id},
            headers=self.headers
        )
        content_vote = json.loads(response_vote.content)
        self.assertResponseNoErrors(response_vote)

        # Ensure that the vote response includes the link data
        assert content_vote['data']['createVote']['link']['id'] == str(self.link1.id)
        assert content_vote['data']['createVote']['link']['url'] == self.link1.url
        assert content_vote['data']['createVote']['link']['description'] == self.link1.description

        # Query links to check if the link data is correctly returned after voting
        response_links = self.query(
            '''
            query MyQuery {
                links {
                    description
                    id
                    url
                }
            }
            '''
        )
        content_links = json.loads(response_links.content)
        self.assertResponseNoErrors(response_links)

        # Check if the link we voted on is in the links list
        links_data = content_links['data']['links']
        assert any(link['id'] == str(self.link1.id) for link in links_data)