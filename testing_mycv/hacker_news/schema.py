import graphene
import graphql_jwt

import certificates.schema
import header
import header.schema
import links.schema
import skills
import skills.schema
import users.schema
import education.schema
import languages.schema
import workexperience.schema
import interests.schema

class Query(languages.schema.Query, education.schema.Query, certificates.schema.Query, workexperience.schema.Query, interests.schema.Query, skills.schema.Query , header.schema.Query, users.schema.Query, links.schema.Query, graphene.ObjectType):
    pass

class Mutation(languages.schema.Mutation, education.schema.Mutation, certificates.schema.Mutation, workexperience.schema.Mutation, interests.schema.Mutation, skills.schema.Mutation, header.schema.Mutation ,users.schema.Mutation, links.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
