import graphene
from graphene_django import DjangoObjectType
from .models import Education
from users.schema import UserType
from django.db.models import Q

class EducationType(DjangoObjectType):
    class Meta:
        model = Education

class Query(graphene.ObjectType):
    degrees = graphene.List(EducationType, search=graphene.String())
    degreeById = graphene.Field(EducationType, idEducation=graphene.Int())

    def resolve_degrees(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            return Education.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(degree__icontains=search)
            )
            return Education.objects.filter(filter)
        
    def resolve_degreeById(self, info, idEducation, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        filter = (
            Q(posted_by=user) & Q(id = idEducation)
        )
        return Education.objects.filter(filter).first()
        
class CreateEducation(graphene.Mutation):
    idEducation   = graphene.Int()
    degree     = graphene.String()
    university = graphene.String()
    startDate = graphene.Date()
    endDate   = graphene.Date()
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        idEducation= graphene.Int()  
        degree     = graphene.String()
        university = graphene.String()
        startDate = graphene.Date()
        endDate   = graphene.Date()

    #3
    def mutate(self, info, idEducation, degree, university, startDate, endDate):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in !');
        print(user)

        currentEducation = Education.objects.filter(id=idEducation).first()
        print (currentEducation)

        education = Education(
            degree     = degree,
            university = university,
            startDate = startDate,
            endDate   = endDate,
            posted_by  = user
            )
        
        if currentEducation:
            education.id = currentEducation.id

        education.save()

        return CreateEducation(
            idEducation  = education.id,
            degree     = education.degree,
            university = education.university,
            startDate = education.startDate,
            endDate   = education.endDate,
            posted_by  = education.posted_by
        )

class DeleteEducation(graphene.Mutation):
    idEducation=graphene.Int()

    #2 
    class Arguments: 
        idEducation= graphene.Int()

    #3
    def mutate(self, info, idEducation):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        currentEducation = Education.objects.filter(id=idEducation).first()
        print (currentEducation)

        if not currentEducation:
            raise Exception('Invalid Education id')
        
        currentEducation.delete()

        return DeleteEducation(
            idEducation = idEducation,
        )
        
#4
class Mutation(graphene.ObjectType):
    create_education = CreateEducation.Field()
    delete_education = DeleteEducation.Field()

schema = graphene.Schema(mutation=Mutation)

