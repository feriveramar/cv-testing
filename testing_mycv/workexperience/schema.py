import graphene
from graphene_django import DjangoObjectType
from .models import WorkExperience
from users.schema import UserType
from django.db.models import Q

class WorkExperienceType(DjangoObjectType):
    class Meta:
        model = WorkExperience

class Query(graphene.ObjectType):
    positions = graphene.List(WorkExperienceType, search=graphene.String())
    positionById = graphene.Field(WorkExperienceType, idWorkExperience=graphene.Int())

    def resolve_positions(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            return WorkExperience.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(position__icontains=search)
            )
            return WorkExperience.objects.filter(filter)
        
    def resolve_positionById(self, info, idWorkExperience, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        filter = (
            Q(posted_by=user) & Q(id = idWorkExperience)
        )
        return WorkExperience.objects.filter(filter).first()
        
class CreateWorkExperience(graphene.Mutation):
    idWorkExperience   = graphene.Int()
    position     = graphene.String()
    company = graphene.String()
    location = graphene.String()
    description = graphene.String()
    startDate = graphene.Date()
    endDate   = graphene.Date()
    achievements = graphene.List(graphene.String)
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        idWorkExperience= graphene.Int()  
        position     = graphene.String()
        company = graphene.String()
        location = graphene.String()
        description = graphene.String()
        startDate = graphene.Date()
        endDate   = graphene.Date()
        achievements = graphene.List(graphene.String)

    #3
    def mutate(self, info, idWorkExperience, position, company,  location, description , startDate, endDate, achievements):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in !');
        print(user)

        currentWorkExperience = WorkExperience.objects.filter(id=idWorkExperience).first()
        print (currentWorkExperience)

        workExperience = WorkExperience(
            company = company,
            position = position,
            location = location,
            description = description,
            startDate = startDate,
            endDate   = endDate,
            posted_by  = user,
            achievements = achievements
            )
        
        if currentWorkExperience:
            workExperience.id = currentWorkExperience.id

        workExperience.save()

        return CreateWorkExperience(
            idWorkExperience  = workExperience.id,
            company = workExperience.company,
            position = workExperience.position,
            location = workExperience.location,
            description = workExperience.description,
            startDate = workExperience.startDate,
            endDate   = workExperience.endDate,
            achievements = workExperience.achievements,
            posted_by  = workExperience.posted_by
        )

class DeleteWorkExperience(graphene.Mutation):
    idWorkExperience=graphene.Int()

    #2 
    class Arguments: 
        idWorkExperience= graphene.Int()

    #3
    def mutate(self, info, idWorkExperience):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        currentWorkExperience = WorkExperience.objects.filter(id=idWorkExperience).first()
        print (currentWorkExperience)

        if not currentWorkExperience:
            raise Exception('Invalid WorkExperience id')
        
        currentWorkExperience.delete()

        return DeleteWorkExperience(
            idWorkExperience = idWorkExperience,
        )
        
#4
class Mutation(graphene.ObjectType):
    create_workExperience = CreateWorkExperience.Field()
    delete_workExperience = DeleteWorkExperience.Field()


schema = graphene.Schema(mutation=Mutation)
