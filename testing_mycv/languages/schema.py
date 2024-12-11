import graphene
from graphene_django import DjangoObjectType
from .models import Languages
from users.schema import UserType
from django.db.models import Q

class LanguagesType(DjangoObjectType):
    class Meta:
        model = Languages

class Query(graphene.ObjectType):
    languages = graphene.List(LanguagesType, search=graphene.String())
    languageById = graphene.Field(LanguagesType, idLanguages=graphene.Int())

    def resolve_languages(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            return Languages.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(language__icontains=search)
            )
            return Languages.objects.filter(filter)
        
    def resolve_languageById(self, info, idLanguages, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        filter = (
            Q(posted_by=user) & Q(id = idLanguages)
        )
        return Languages.objects.filter(filter).first()
        
class CreateLanguages(graphene.Mutation):
    idLanguages   = graphene.Int()
    language     = graphene.String()
    level = graphene.String()
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        idLanguages= graphene.Int()  
        language     = graphene.String()
        level = graphene.String()


    #3
    def mutate(self, info, idLanguages, language, level):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in !');
        print(user)

        currentLanguages = Languages.objects.filter(id=idLanguages).first()
        print (currentLanguages)

        languages = Languages(
            language = language,
            level = level,
            posted_by  = user
            )
        
        if currentLanguages:
            languages.id = currentLanguages.id

        languages.save()

        return CreateLanguages(
            idLanguages  = languages.id,
            language    = languages.language,
            level = languages.level,
            posted_by  = languages.posted_by
        )

class DeleteLanguages(graphene.Mutation):
    idLanguages=graphene.Int()

    #2 
    class Arguments: 
        idLanguages= graphene.Int()

    #3
    def mutate(self, info, idLanguages):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        currentLanguages = Languages.objects.filter(id=idLanguages).first()
        print (currentLanguages)

        if not currentLanguages:
            raise Exception('Invalid Language id')
        
        currentLanguages.delete()

        return DeleteLanguages(
            idLanguages = idLanguages,
        )
        
#4
class Mutation(graphene.ObjectType):
    create_Languages = CreateLanguages.Field()
    delete_Languages = DeleteLanguages.Field()

schema = graphene.Schema(mutation=Mutation)