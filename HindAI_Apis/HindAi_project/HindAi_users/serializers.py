from rest_framework import serializers
from .models import HindAIUser, UserProfile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = HindAIUser
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = HindAIUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'bio', 'twitter_handle', 'facebook_handle', 
                  'linkedin_handle', 'instagram_handle', 'github_handle', 
                  'location', 'website', 'profile_picture')
