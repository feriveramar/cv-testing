import graphene
from graphene_django import DjangoObjectType
from .models import Interests
from users.schema import UserType
from django.db.models import Q

class InterestsType(DjangoObjectType):
    class Meta:
        model = Interests

class Query(graphene.ObjectType):
    interests = graphene.List(InterestsType, search=graphene.String())
    interestById = graphene.Field(InterestsType, idInterests=graphene.Int())

    def resolve_interests(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            return Interests.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(name__icontains=search)
            )
            return Interests.objects.filter(filter)
        
    def resolve_interestById(self, info, idInterests, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        filter = (
            Q(posted_by=user) & Q(id = idInterests)
        )
        return Interests.objects.filter(filter).first()
        
class CreateInterests(graphene.Mutation):
    idInterests   = graphene.Int()
    name     = graphene.String()
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        idInterests= graphene.Int()  
        name  = graphene.String()



    #3
    def mutate(self, info, idInterests, name):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in !');
        print(user)

        currentInterests = Interests.objects.filter(id=idInterests).first()
        print (currentInterests)

        interests = Interests(
            name = name,
            posted_by  = user
            )
        
        if currentInterests:
            interests.id = currentInterests.id

        interests.save()

        return CreateInterests(
            idInterests  = interests.id,
            name    = interests.name,
            posted_by  = interests.posted_by
        )

class DeleteInterests(graphene.Mutation):
    idInterests=graphene.Int()

    #2 
    class Arguments: 
        idInterests= graphene.Int()

    #3
    def mutate(self, info, idInterests):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        currentInterests = Interests.objects.filter(id=idInterests).first()
        print (currentInterests)

        if not currentInterests:
            raise Exception('Invalid Interests id')
        
        currentInterests.delete()

        return DeleteInterests(
            idInterests = idInterests,
        )
        
#4
class Mutation(graphene.ObjectType):
    create_Interests = CreateInterests.Field()
    delete_Interests = DeleteInterests.Field()

schema = graphene.Schema(mutation=Mutation)
