from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import HelloModel, MonteCarloIntegrationModel


class HelloSerializer(ModelSerializer):
    class Meta:
        model = HelloModel
        fields = "__all__"

    def create(self, validated_data):
        hello = HelloModel.objects.create(text=validated_data["text"])
        return hello


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password")

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data["username"], password=validated_data["password"])
        return user

    def get(self, validated_data):
        user = User.objects.get(username=validated_data["username"], password=validated_data["password"])
        return user


class MonteCarloSerializer(serializers.ModelSerializer):
    graphic_url = serializers.SerializerMethodField()

    class Meta:
        model = MonteCarloIntegrationModel
        fields = ['function', 'lower_bound', 'upper_bound', 'estimated_area', 'graphic_url', 'timestamp', 'time_needed']

    def get_graphic_url(self, obj):
        return obj.get_graphic()