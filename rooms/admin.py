from django.contrib import admin
from .models import Room, Amenity

# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "rooms",
        "kind",
        "total_amenities",
        "owner",
        "created_at",
    )

    list_filter = (
        "country",
        "pet_friendly",
        "kind",
        "owner",
        "amenities",
        "created_at",
        "updated_at",
    )

    def total_amenities(self, room):
        return room.amenities.count()


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
