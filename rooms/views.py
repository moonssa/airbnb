from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from django.db import transaction
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
)
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Amenity, Room
from categories.models import Category
from .serializers import (
    RoomDetailSerializer,
    RoomListSerializer,
    AmenitySerializer,
)
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from bookings.models import Booking
from bookings.serializers import PublicBookingSerializer, CreateRoomBookingSerializer


class Amenities(APIView):
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(
            all_amenities,
            many=True,
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(AmenitySerializer(amenity).data)
        else:
            return Response(serializer.errors)


class AmenityDetail(APIView):
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        return Response(
            AmenitySerializer(self.get_object(pk)).data,
        )

    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            return Response(
                AmenitySerializer(serializer.save()).data,
            )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Rooms(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(
            all_rooms,
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)

    def post(self, request):
        # print(dir(request.user))

        serializer = RoomDetailSerializer(data=request.data)
        if serializer.is_valid():
            print(
                "*** requested Data",
                request.data,
            )
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError("Category is required")

            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                    raise ParseError("The category  kind should be 'rooms'")

            except Category.DoesNotExist:
                raise ParseError("Category Not found")
            print(request.data.get("amenities"))

            try:
                with transaction.atomic():

                    room = serializer.save(
                        owner=request.user,
                        category=category,
                    )

                    amenities = request.data.get("amenities")
                    for amenity_pk in amenities:

                        amenity = Amenity.objects.get(pk=amenity_pk)
                        room.amenities.add(amenity)

                    serializer = RoomDetailSerializer(room)
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Ammenity not found")
        else:
            return Response(serializer.errors)


class RoomDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(
            room,
            context={"request": request},
        )
        return Response(serializer.data)

    def delete(self, request, pk):
        room = self.get_object(pk)

        if room.owner != request.user:
            raise PermissionDenied

        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def put(self, request, pk):
        room = self.get_object(pk)

        if room.owner != request.user:
            raise PermissionDenied

        serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            return Response(
                RoomDetailSerializer(serializer.save()).data,
            )
        else:
            Response(serializer.errors)


class RoomReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        print(request.query_params)
        try:
            page = request.query_params.get("page", 1)  # 기본값지정
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size

        print("***", page)
        room = self.get_object(pk)
        serializer = ReviewSerializer(
            room.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):

        seriallizer = ReviewSerializer(data=request.data)
        if seriallizer.is_valid():
            review = seriallizer.save(
                user=request.user,
                room=self.get_object(pk),
            )
            seriallizer = ReviewSerializer(review)
            return Response(seriallizer.data)


class RoomAmenities(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page) - 1
        except ValueError:
            page = 0

        page_size = settings.PAGE_SIZE
        start = page * page_size
        end = start + page_size

        room = self.get_object(pk)
        serializer = AmenitySerializer(
            room.amenities.all()[start:end],
            many=True,
        )
        return Response(serializer.data)


class RoomPhotos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        room = self.get_object(pk)

        if request.user != room.owner:
            raise PermissionDenied

        serializer = PhotoSerializer(data=request.data)

        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class RoomBookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        now = timezone.localtime(timezone.now()).date()

        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__gt=now,
        )
        # DB를 access하지 않고..
        # bookings = Booking.objects.filter(room__pk = pk)

        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        room = self.get_object(pk)
        serializer = CreateRoomBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(
                room=room,
                user=request.user,
                kind=Booking.BookingKindChoices.ROOM,
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
