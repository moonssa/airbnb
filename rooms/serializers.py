from rest_framework import serializers


from .models import Amenity, Room
from users.serializers import TinyUserSerializer
from categories.serializers import (
    CategorySerializer,
)
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from wishlists.models import Wishlist


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = (
            "name",
            "description",
        )


class RoomDetailSerializer(serializers.ModelSerializer):
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    # customize serial field
    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = "__all__"

    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]
        return room.owner == request.user

    def get_is_liked(self, room):
        request = self.context["request"]

        # user가 만든 위시리스트중에서 찾는 룸아이디가 들어있는 룸리스트를 포함힌 위시리스트를 찾는다.
        return Wishlist.objects.filter(
            user=request.user,
            rooms__pk=room.pk,
        ).exists()

    # def create(self, validated_data):
    #     print("-----------", validated_data)
    #     return


class RoomListSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "rating",
            "is_owner",
            "photos",
        )

    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]
        return room.owner == request.user
