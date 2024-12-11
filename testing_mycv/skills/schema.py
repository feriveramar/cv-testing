import graphene
from graphene_django import DjangoObjectType
from .models import Skills
from users.schema import UserType
from django.db.models import Q

class SkillsType(DjangoObjectType):
    class Meta:
        model = Skills

class Query(graphene.ObjectType):
    skills = graphene.List(SkillsType, search=graphene.String())
    skillById = graphene.Field(SkillsType, idSkills=graphene.Int())

    def resolve_skills(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            return Skills.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(name__icontains=search)
            )
            return Skills.objects.filter(filter)
        
    def resolve_skillById(self, info, idSkills, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        filter = (
            Q(posted_by=user) & Q(id = idSkills)
        )
        return Skills.objects.filter(filter).first()
        
class CreateSkills(graphene.Mutation):
    idSkills   = graphene.Int()
    name     = graphene.String()
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        idSkills= graphene.Int()  
        name  = graphene.String()

    #3
    def mutate(self, info, idSkills, name):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in !');
        print(user)

        currentSkills = Skills.objects.filter(id=idSkills).first()
        print (currentSkills)

        skills = Skills(
            name = name,
            posted_by  = user
            )
        
        if currentSkills:
            skills.id = currentSkills.id

        skills.save()

        return CreateSkills(
            idSkills  = skills.id,
            name    = skills.name,
            posted_by  = skills.posted_by
        )

class DeleteSkills(graphene.Mutation):
    idSkills=graphene.Int()

    #2 
    class Arguments: 
        idSkills= graphene.Int()

    #3
    def mutate(self, info, idSkills):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        currentSkills = Skills.objects.filter(id=idSkills).first()
        print (currentSkills)

        if not currentSkills:
            raise Exception('Invalid Skills id')
        
        currentSkills.delete()

        return DeleteSkills(
            idSkills = idSkills,
        )
        
#4
class Mutation(graphene.ObjectType):
    create_Skills = CreateSkills.Field()
    delete_Skills = DeleteSkills.Field()

schema = graphene.Schema(mutation=Mutation)
