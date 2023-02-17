from django.contrib import admin
from .models import Review

# Register your models here.


class RatingFilter(admin.SimpleListFilter):
    title = "Filter by Rating"
    parameter_name = "rating"

    def lookups(self, request, model_admin):
        return [
            ("good", "GOOD"),
            ("bad", "BAD"),
        ]

    def queryset(self, request, reviews):
        print(self.value())
        evaluation = self.value()
        if evaluation == "good":
            return reviews.filter(rating__gte=3)
        elif evaluation == "bad":
            return reviews.filter(rating__lt=3)
        else:
            return reviews


class WordFilter(admin.SimpleListFilter):
    title = "Filter by Words !"
    parameter_name = "word"  # url 에 디스플레이 되는 이름.

    def lookups(self, request, model_admin):  # model_admin 은 ReviewAdmin을 받는다.
        return [
            ("great", "GREAT"),
            ("good", "GOOD"),
            ("awesome", "AWESOME"),
            ("bad", "BAD"),
        ]

    def queryset(self, request, reviews):
        # 마지막 파라미터는 필터링할 리뷰

        # print(reviews)
        # print("****", self.value())
        word = self.value()
        if word:
            return reviews.filter(payload__contains=word)
        else:
            reviews


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "payload",
    )

    list_filter = (
        WordFilter,
        RatingFilter,
        "rating",
        "user__is_host",
        "room__category",
        "room__pet_friendly",
    )
