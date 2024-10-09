from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.authentication import authenticate
from rest_framework.exceptions import ValidationError

get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model, handling the creation and validation of users.

    Fields:
        username: the unique name of the user.
        password: the password of the user.
        password2: the validation password similar to the first password.
        email: the unique email of the user.
        profile_picture: the profile picture of the user.
    """
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'password2', 'email', 'profile_picture']

    def validate(self, data):
        """Checks if the two passwords match"""

        if data['password'] != data['password2']:
            raise ValueError({'password': 'Passwords must match'})
        return data

    def create(self, validated_data):
        #Remove password2 during the creation of the user
        validated_data.pop('password2') 

        user = get_user_model().objects.create(username = validated_data['username'],
                                               email = validated_data['email'],
                                               profile_picture = validated_data.get('profile_picture', None)
                                               )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user and generating an authentication token.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the provided credentials (username and password).
        
        Parameters:
        data (dict): The data containing 'username' and 'password' fields.

        Returns:
        dict: The validated data with the authenticated user added.

        Raises:
        ValidationError: If the username or password is invalid.
        """
        username = data.get('username')
        password = data.get('password')

        # Authenticate the user based on the provided credentials
        user = authenticate(username=username, password=password)

        # Raise error if authentication fails
        if user is None:
            raise ValidationError({'message': 'Invalid username or password'})
        
        # Add the authenticated user to the validated data
        data['user'] = user
        return data
    
    def to_representation(self, instance):
        """
        Customizes the representation of the serialized data.

        Returns a dictionary containing a success message and the user's authentication token.
        """
        # Get the authenticated user from the validated data
        user = instance['user']

        # Get or create a token for the authenticated user
        token, _ = Token.objects.get_or_create(user=user)

        # Return a success message and the authentication token
        return {
            'message': 'Login successful',
            'Token': token.key
        }

       
class ProfileSerializer(serializers.ModelSerializer):
    """
        Serializer for retrieving and modifying the user data.

        Fields to modify:
            username: username of the current user.
            profile_picture: profile picture of the user.
            followers_count: number of current user's followers.
    """
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'profile_picture', 'followers_count'] 

    #Counts and returns the number of followers
    def get_followers_count(self, obj):
        return obj.followers.count()

class AccountDestroySerializer(serializers.ModelSerializer):
    """
    Serializer to delete the user data from the database by their username.
    """
    class Meta:
        model = get_user_model()
        fields = ['username']

class FollowingSerializer(serializers.ModelSerializer):
    """
        Serializer for the following model, handling the following of a user.

        Fields: 
            username: name of the user to follow.
            profile_picture: profile picture of the user to follow.
    """
    class Meta:
        model = get_user_model()
        fields = ['username', 'profile_picture']

class FollowersSerializer(serializers.ModelSerializer):
    """
        Serializer for the followers model, to see current user's followers.
        
        Fields:
            username: username of the follower.
            profile_picture: profile picture of the follower.
    """
    class Meta:
        model = get_user_model()
        fields = ['username', 'profile_picture']


    

