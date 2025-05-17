from rest_framework import serializers
from .models import *

# Serializer pour l'Action
class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'user', 'action_type', 'timestamp', 'content_type', 'object_id', 'object_repr']


# Serializer pour le CodeCenter
class CodeCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeCenter
        fields = ['id', 'code', 'name', 'description', 'created_at', 'updated_at']


# Serializer pour l'image du produit
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'description']



# Serializer pour le Role
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


# Serializer pour le User
class UserListSerializer(serializers.ModelSerializer):
    entreprise = CodeCenterSerializer(many=False, read_only=True)
    role = RoleSerializer(many=False, read_only=True)
    class Meta:
        model = User
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    actions = ActionSerializer(many=True, read_only=True)
    entreprise = serializers.PrimaryKeyRelatedField(queryset=CodeCenter.objects.all())  # Attente d'un ID pour l'entreprise
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())  # Attente d'un ID pour le rôle

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        # Extraire les autres champs et créer l'utilisateur
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Assure-toi de hacher le mot de passe
        user.save()
        return user
        
    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     user = User.objects.create(**validated_data)
    #     user.set_password(password)  # Assure-toi de hacher le mot de passe
    #     user.save()
    #     return user


# Serializer pour le Product
class ProductSerializer(serializers.ModelSerializer):
    # Accepte des images sous forme de fichiers mais stocke leurs ID après création
    many_pictures = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    images = serializers.SerializerMethodField()  # Pour lire les images associées

    class Meta:
        model = Product
        fields = ['id', 'user', 'name', 'price', 'description', 'availability', 'photo', 'many_pictures', 'images']

    def get_images(self, obj):
        # Récupère l'URL des images associées au produit
        return [{'id': img.id, 'image': img.image.url} for img in obj.many_pictures.all()]

    def create(self, validated_data):
        # Récupérer les images du formulaire (liste de fichiers)
        images_data = self.context['request'].FILES.getlist('many_pictures')

        # Supprimer les données d'images pour éviter le conflit
        validated_data.pop('many_pictures', None)

        # Créer le produit sans les images d'abord
        product = Product.objects.create(**validated_data)

        # Créer et associer les images au produit
        for image in images_data:
            # Créer une image
            img_obj = ProductImage.objects.create(image=image)
            product.many_pictures.add(img_obj)  # Associer l'image au produit

        return product
    
# class ProductSerializer(serializers.ModelSerializer):
    
#     user = UserSerializer(many=False)  # Serializer de l'utilisateur
#     many_pictures = ProductImageSerializer(many=True)

#     class Meta:
#         model = Product
#         fields = ['id', 'user', 'name', 'price', 'description', 'availability', 'photo', 
#                   'many_pictures', 'created_at', 'updated_at']
        
        
class ProductFirstSerializer(serializers.ModelSerializer):
    many_pictures = serializers.PrimaryKeyRelatedField(queryset=ProductImage.objects.all(), many=True)

    class Meta:
        model = Product
        fields = '__all__'


# Serializer pour le Subscription
class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'name', 'description', 'start_date', 'end_date', 'status']
