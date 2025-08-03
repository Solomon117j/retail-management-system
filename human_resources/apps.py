from django.apps import AppConfig


class HumanResourcesConfig(AppConfig):
    name = 'human_resources'
    dependencies = ['store_management']
