import graphene
from graphene_django import DjangoObjectType
from .models import Header
from users.schema import UserType

class HeaderType(DjangoObjectType):
    class Meta:
        model = Header

class Query(graphene.ObjectType):
    # Fetch the singleton Header instance
    header = graphene.Field(HeaderType)

    def resolve_header(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        # Fetch the singleton Header instance
        header = Header.objects.first()
        if not header:
            raise Exception('Header not found!')  # Handle the absence of the Header
        return header
        
class CreateOrUpdateHeader(graphene.Mutation):
    idHeader = graphene.Int()
    url = graphene.String()
    title = graphene.String()
    description = graphene.String()
    phone = graphene.String()
    address = graphene.String()
    email = graphene.String()
    socialmedia = graphene.String()
    posted_by = graphene.Field(UserType)

    # Arguments for creating or updating the header
    class Arguments:
        url= graphene.String()
        title = graphene.String()
        description = graphene.String()
        phone = graphene.String()
        address = graphene.String()
        email = graphene.String()
        socialmedia = graphene.String()

    def mutate(self, info, title, description, phone, address, email, socialmedia, url):
        user = info.context.user or None
        if user.is_anonymous:
            raise Exception('Not logged in!')
        print(user)

        # Fetch or create the singleton Header
        header, created = Header.objects.get_or_create(id=1, defaults={
            'title': title,
            'url': url,
            'description': description,
            'phone' : phone,
            'address': address,
            'email': email,
            'socialmedia': socialmedia,
            'posted_by': user,
        })

        if not created:  # If the Header already exists, update its fields
            header.title = title
            header.url = url
            header.description = description
            header.phone = phone
            header.address = address
            header.email = email
            header.socialmedia = socialmedia
            header.posted_by = user
            header.save()

        return CreateOrUpdateHeader(
            idHeader=header.id,
            url=header.url,
            title=header.title,
            description=header.description,
            phone= header.phone,
            address=header.address,
            email=header.email,
            socialmedia=header.socialmedia,
            posted_by=header.posted_by,
        )

class Mutation(graphene.ObjectType):
    create_or_update_header = CreateOrUpdateHeader.Field()

schema = graphene.Schema(mutation=Mutation)