from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("barber/<int:pk>/", views.barber_detail, name="barber_detail"),
    path("barber/<int:pk>/confirm/", views.booking_confirm, name="booking_confirm"),
    path("booking/<int:booking_id>/success/", views.booking_success, name="booking_success"),
    path("booking/action/<str:token>/<str:action>/", views.booking_action, name="booking_action"),
    path("bronlarim/", views.my_bookings, name="my_bookings"),
]
