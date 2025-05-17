from rest_framework import generics
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action





# Vue pour les Actions
class ActionListCreate(generics.ListCreateAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated]

class ActionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [IsAuthenticated]

# Vue pour les CodeCenters
class CodeCenterListCreate(generics.ListCreateAPIView):
    queryset = CodeCenter.objects.all()
    serializer_class = CodeCenterSerializer
    permission_classes = [IsAuthenticated]

class CodeCenterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CodeCenter.objects.all()
    serializer_class = CodeCenterSerializer
    permission_classes = [IsAuthenticated]

# Vue pour les ProductImages
class ProductImageListCreate(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

class ProductImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

# Vue pour les Roles
class RoleListCreate(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

class RoleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

# Vue pour les Users
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entreprise']

    def get_queryset(self):
        entreprise_id = self.request.query_params.get('entreprise_id')

        # Si le paramètre n'est pas un entier valide, renvoie une erreur
        try:
            entreprise_id = int(entreprise_id)  # Essaye de convertir en entier
        except (TypeError, ValueError):
            return User.objects.none()  # Retourne une réponse vide si l'ID n'est pas valide

        # Applique le filtre sur le queryset
        return self.queryset.filter(entreprise_id=entreprise_id)
    

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    from rest_framework.permissions import AllowAny
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entreprise']



# Vue pour les Products
class ProductListCreate(generics.ListCreateAPIView):
    from rest_framework.permissions import AllowAny
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entreprise']

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')

        # Si le paramètre n'est pas un entier valide, renvoie une erreur
        try:
            user_id = int(user_id)  # Essaye de convertir en entier
        except (TypeError, ValueError):
            return User.objects.none()  # Retourne une réponse vide si l'ID n'est pas valide

        # Applique le filtre sur le queryset
        return self.queryset.filter(user=user_id)

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    from rest_framework.permissions import AllowAny
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entreprise']
    
    def perform_destroy(self, instance):
        from django.contrib.contenttypes.models import ContentType

        user = self.request.user  # Récupère l'utilisateur qui effectue la suppression
        Action.objects.create(
            user=user,
            action_type='delete',
            content_type=ContentType.objects.get_for_model(instance),
            object_repr=str(instance.name),
        )
        instance.delete()

# Vue pour les Subscriptions
class SubscriptionListCreate(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entreprise']

class SubscriptionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entreprise']



from rest_framework_simplejwt.tokens import RefreshToken, TokenError
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"detail": "Token de rafraîchissement manquant."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Ajoute le token à la blacklist
            return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"detail": "Token invalide ou déjà blacklisté."}, status=status.HTTP_400_BAD_REQUEST)






class CustomTokenObtainPairView(APIView):
    from rest_framework.permissions import AllowAny
    permission_classes = [AllowAny] 

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email et mot de passe sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if user is None:
            return Response({"detail": "L'utilisateur avec cet email n'existe pas."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            # Création du token
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token.set_exp(lifetime=timedelta(hours=1))

            # Calcul du temps écoulé depuis la dernière connexion
            last_login_time = user.last_login if user.last_login else user.date_joined
            time_since_last_login = now() - last_login_time

            # Mise à jour de la dernière connexion
            user.last_login = now()
            user.save(update_fields=['last_login'])

            return Response({
                'message': "Connexion réussie !",
                'access': str(access_token),
                'refresh': str(refresh),
                'user': UserListSerializer(user).data,  # Utilisation du serializer pour envoyer tous les champs du modèle
                'time_since_last_login': str(time_since_last_login)
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)