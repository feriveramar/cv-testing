import graphene
from graphene_django import DjangoObjectType
from .models import Certificates
from users.schema import UserType
from django.db.models import Q

class CertificatesType(DjangoObjectType):
    class Meta:
        model = Certificates

class Query(graphene.ObjectType):
    certificates = graphene.List(CertificatesType, search=graphene.String())
    certificateById = graphene.Field(CertificatesType, idCertificates=graphene.Int())

    def resolve_certificates(self, info, search=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)
        if (search=="*"):
            filter = (
                Q(posted_by=user)
            )
            return Certificates.objects.filter(filter)[:10]
        else:
            filter = (
                Q(posted_by=user) & Q(title__icontains=search)
            )
            return Certificates.objects.filter(filter)
        
    def resolve_certificateById(self, info, idCertificates, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        filter = (
            Q(posted_by=user) & Q(id = idCertificates)
        )
        return Certificates.objects.filter(filter).first()
        
class CreateCertificates(graphene.Mutation):
    idCertificates   = graphene.Int()
    title     = graphene.String()
    institution = graphene.String()
    year = graphene.Int()
    posted_by = graphene.Field(UserType)

    #2
    class Arguments:
        idCertificates = graphene.Int()  
        title     = graphene.String()
        institution = graphene.String()
        year = graphene.Int()
        

    #3
    def mutate(self, info, idCertificates, title, institution, year):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in !');
        print(user)

        currentCertificates = Certificates.objects.filter(id=idCertificates).first()
        print (currentCertificates)

        certificates = Certificates(
            title     = title,
            institution = institution,
            year = year,
            posted_by  = user
            )
        
        if currentCertificates:
            certificates.id = currentCertificates.id

        certificates.save()

        return CreateCertificates(
            idCertificates  = certificates.id,
            title = certificates.title,
            institution = certificates.institution,
            year = certificates.year,
            posted_by  = certificates.posted_by
        )

class DeleteCertificates(graphene.Mutation):
    idCertificates=graphene.Int()

    #2 
    class Arguments: 
        idCertificates= graphene.Int()

    #3
    def mutate(self, info, idCertificates):
        user = info.context.user or None

        if user.is_anonymous:
            raise Exception('Not logged in!')
        print (user)

        currentCertificates = Certificates.objects.filter(id=idCertificates).first()
        print (currentCertificates)

        if not currentCertificates:
            raise Exception('Invalid Certificates id')
        
        currentCertificates.delete()

        return DeleteCertificates(
            idCertificates = idCertificates,
        )
        
#4
class Mutation(graphene.ObjectType):
    create_Certificates = CreateCertificates.Field()
    delete_Certificates = DeleteCertificates.Field()

schema = graphene.Schema(mutation=Mutation)
