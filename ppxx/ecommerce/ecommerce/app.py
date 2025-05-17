# apps.py
from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    name = 'ecommerce'

    def ready(self):
        import ecommerce.signal # Assure-toi que le chemin est correct
