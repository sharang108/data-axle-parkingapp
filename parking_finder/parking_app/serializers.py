from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from parking_app.models import Parking

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ("username", "password", "email", "phone")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            phone=validated_data.get("phone", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ParkingSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source="geometry")
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Parking
        fields = ("id", "tag", "location", "user")
