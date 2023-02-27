from django.urls import path
from . import views

# config/urls.py에서 rooms url 확인 가능
urlpatterns = [
    path("amenities/", views.Amenities.as_view()),
    path(
        "amenities/<int:pk>",
        views.AmenityDetail.as_view(),
    ),
]
