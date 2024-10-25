from rest_framework import serializers
from .models import Posts
from django.contrib.auth.models import User


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'author']
        read_only_fields = ['author']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        # Создаем пользователя с хешированным паролем
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


