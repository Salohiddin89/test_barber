from django.contrib import admin
from django.contrib import messages

from .models import Barber, Booking


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "full_name", "years_experience", "work_start", "work_end", "is_active")
    list_filter = ("is_active",)
    search_fields = ("shop_name", "first_name", "last_name", "specialty")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("client_name", "barber", "start_time", "phone_number", "status")
    list_filter = ("status", "barber")
    search_fields = ("client_name", "phone_number", "barber__first_name", "barber__last_name")
    list_editable = ("status",)

    def save_model(self, request, obj, form, change):
        accepted_exists = Booking.objects.filter(
            barber=obj.barber,
            start_time=obj.start_time,
            status__in=[Booking.Status.ACCEPTED, Booking.Status.COMPLETED],
        ).exclude(pk=obj.pk)

        if obj.status == Booking.Status.ACCEPTED and accepted_exists.exists():
            self.message_user(
                request,
                "Bu vaqt allaqachon boshqa tasdiqlangan bron tomonidan band qilingan.",
                level=messages.ERROR,
            )
            return

        super().save_model(request, obj, form, change)

        if obj.status == Booking.Status.ACCEPTED:
            Booking.objects.filter(
                barber=obj.barber,
                start_time=obj.start_time,
                status=Booking.Status.PENDING,
            ).exclude(pk=obj.pk).update(status=Booking.Status.CANCELLED)
