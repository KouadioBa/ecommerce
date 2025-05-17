from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


def get_default_user():
    User = get_user_model()
    return User.objects.first() if User.objects.exists() else None


from django.conf import settings

class Actionable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(class)s_actions")
    action_type = models.CharField(
        max_length=10,
        choices=[
            ("CREATE", "Création"),
            ("UPDATE", "Mise à jour"),
            ("DELETE", "Suppression"),
        ],
        default="UPDATE",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    content_type = models.CharField(max_length=255, default="")
    object_repr = models.CharField(max_length=255, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.user} {self.action_type} {self.content_type}"


class Action(Actionable):
    pass


class CodeCenter(models.Model):
    code = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Si l'objet est nouveau
            if not self.code:
                prefix = "CC"
                
                # Récupérer le dernier code généré
                last_code = CodeCenter.objects.order_by('-id').first()

                if last_code and last_code.code:
                    try:
                        last_code_number = int(last_code.code[2:])  # Extraire seulement la partie numérique
                        new_code = last_code_number + 1
                    except ValueError:
                        new_code = 1  # Si une erreur se produit, on recommence à 1
                else:
                    new_code = 1  # Premier enregistrement

                # Format du code avec trois chiffres (ex: CC001, CC002, etc.)
                self.code = f"{prefix}{new_code:03}"

        super(CodeCenter, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"



class ProductImage(models.Model):
    image = models.ImageField(upload_to="product_images/")
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.image} - {self.description}"


class Role(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Le champ email doit être renseigné")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, first_name, last_name, phone, password, **extra_fields)


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    whatsapp_phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    entreprise = models.ForeignKey(CodeCenter, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Nouveaux champs
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    # Carousels  
    first_carousel = models.ImageField(upload_to="carousels/", blank=True, null=True)
    first_carousel_title = models.CharField(max_length=255, blank=True, null=True)
    first_carousel_description = models.TextField(blank=True, null=True)

    second_carousel = models.ImageField(upload_to="carousels/", blank=True, null=True)
    second_carousel_title = models.CharField(max_length=255, blank=True, null=True)
    second_carousel_description = models.TextField(blank=True, null=True)

    third_carousel = models.ImageField(upload_to="carousels/", blank=True, null=True)
    third_carousel_title = models.CharField(max_length=255, blank=True, null=True)
    third_carousel_description = models.TextField(blank=True, null=True)

    # Réseaux sociaux
    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)

    # Lieu d’habitation
    residence = models.CharField(max_length=255, blank=True, null=True)
    structure_name = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # Méthode à ajouter pour corriger l'erreur
    def has_module_perms(self, app_label):
        # Vérifie si l'utilisateur a des permissions pour un module donné
        return self.is_staff  # Par exemple, un utilisateur staff a accès à tous les modules

    def has_perm(self, perm, obj=None):
        """
        Vérifie si l'utilisateur a une permission donnée.
        """
        if self.is_superuser:
            return True  # Un superutilisateur a toutes les permissions
        
        # Vérifie les permissions de l'utilisateur via les groupes et permissions Django
        return self.is_active and self.is_staff  # Seuls les utilisateurs actifs et staff ont les permissions



class Product(Actionable):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    availability = models.BooleanField(default=True)
    photo = models.ImageField(upload_to="products/", blank=True, null=True)
    many_pictures = models.ManyToManyField(ProductImage, related_name="product_images", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entreprise = models.ForeignKey(CodeCenter, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        ordering = ["name"]
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [("active", "Actif"), ("expired", "Expiré")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    entreprise = models.ForeignKey(CodeCenter, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=30)

        self.status = "expired" if datetime.now() > self.end_date else "active"
        super().save(*args, **kwargs)

    def is_active(self):
        return self.status == "active"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        ordering = ["start_date"]


# Signaux pour capturer les actions
@receiver(post_save, sender=get_user_model())
def user_action_post_save(sender, instance, created, **kwargs):
    Action.objects.create(
        user=instance,
        action_type="CREATE" if created else "UPDATE",
        content_type="User",
        object_repr=str(instance.email),
    )


@receiver(pre_delete, sender=get_user_model())
def user_action_pre_delete(sender, instance, **kwargs):
    Action.objects.create(
        user=instance,
        action_type="DELETE",
        content_type="User",
        object_repr=str(instance.email),
    )


@receiver(post_save, sender=Product)
def product_action_post_save(sender, instance, created, **kwargs):
    if instance.user:
        Action.objects.create(
            user=instance.user,
            action_type="CREATE" if created else "UPDATE",
            content_type="Product",
            object_repr=str(instance.name),
        )


@receiver(pre_delete, sender=Product)
def product_action_pre_delete(sender, instance, **kwargs):
    if instance.user:
        Action.objects.create(
            user=instance.user,
            action_type="DELETE",
            content_type="Product",
            object_repr=str(instance.name),
        )
