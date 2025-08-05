from rest_framework import serializers
from users.models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic fields
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'created_at', 'updated_at', 'last_activity')
        read_only_fields = ('created_at', 'updated_at', 'last_activity')

    def create(self, validated_data):
        """Override create method to properly handle password"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
