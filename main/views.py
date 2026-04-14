from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import BookingCreateForm
from .models import Barber, Booking
from .services import send_booking_notification


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def home(request):
    barbers = Barber.objects.filter(is_active=True)
    return render(request, "main/home.html", {"barbers": barbers, "brand_name": settings.SITE_BRAND_NAME})


def barber_detail(request, pk):
    barber = get_object_or_404(Barber, pk=pk, is_active=True)
    selected_slot = request.GET.get("slot", "")
    return render(
        request,
        "main/barber_detail.html",
        {
            "barber": barber,
            "week_slots": barber.get_week_slots(),
            "selected_slot": selected_slot,
        },
    )


@require_http_methods(["GET", "POST"])
def booking_confirm(request, pk):
    barber = get_object_or_404(Barber, pk=pk, is_active=True)
    slot_value = request.GET.get("slot") or request.POST.get("slot")
    if not slot_value:
        messages.error(request, "Avval qulay vaqtni tanlang.")
        return redirect(barber.get_absolute_url())

    try:
        slot_dt = timezone.make_aware(datetime.strptime(slot_value, "%Y-%m-%dT%H:%M"))
    except ValueError:
        messages.error(request, "Tanlangan vaqt noto'g'ri formatda.")
        return redirect(barber.get_absolute_url())

    if slot_dt <= timezone.localtime():
        messages.error(request, "O'tib ketgan vaqtga bron qilib bo'lmaydi.")
        return redirect(barber.get_absolute_url())

    form = BookingCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        session_key = _ensure_session_key(request)
        if Booking.objects.filter(
            barber=barber,
            start_time=slot_dt,
            status__in=[Booking.Status.ACCEPTED, Booking.Status.COMPLETED],
        ).exists():
            messages.error(request, "Bu vaqt band bo'lib qoldi, iltimos boshqa vaqt tanlang.")
            return redirect(barber.get_absolute_url())

        booking = Booking.objects.create(
            barber=barber,
            client_name=form.cleaned_data["client_name"],
            phone_number=form.cleaned_data["phone_number"],
            start_time=slot_dt,
            session_key=session_key,
        )

        send_booking_notification(booking)
        messages.success(
            request,
            f"Bron muvaffaqiyatli yaratildi. Tafsilotlarni Bronlarim sahifasida ko'rishingiz mumkin.",
        )
        return redirect("booking_success", booking_id=booking.pk)

    return render(
        request,
        "main/booking_confirm.html",
        {
            "barber": barber,
            "slot_dt": slot_dt,
            "slot_value": slot_value,
            "form": form,
        },
    )


def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "main/booking_success.html", {"booking": booking})


def booking_action(request, token, action):
    booking = get_object_or_404(Booking, approval_token=token)

    if booking.status in [Booking.Status.CANCELLED, Booking.Status.COMPLETED]:
        message = "Bu bron bo'yicha amal bajarib bo'lingan."
    elif action == "accept":
        has_taken = Booking.objects.filter(
            barber=booking.barber,
            start_time=booking.start_time,
            status__in=[Booking.Status.ACCEPTED, Booking.Status.COMPLETED],
        ).exclude(pk=booking.pk).exists()
        if has_taken:
            booking.status = Booking.Status.CANCELLED
            booking.save(update_fields=["status", "updated_at"])
            message = "Bu vaqt boshqa bron tomonidan band bo'lib qolgan."
        else:
            booking.status = Booking.Status.ACCEPTED
            booking.save(update_fields=["status", "updated_at"])
            Booking.objects.filter(
                barber=booking.barber,
                start_time=booking.start_time,
                status=Booking.Status.PENDING,
            ).exclude(pk=booking.pk).update(status=Booking.Status.CANCELLED)
            message = "Bron tasdiqlandi. Vaqt endi band."
    else:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        message = "Bron rad etildi."

    return render(
        request,
        "main/booking_action_result.html",
        {"booking": booking, "message": message, "action": action},
    )


def my_bookings(request):
    session_key = _ensure_session_key(request)
    upcoming = Booking.objects.filter(
        session_key=session_key,
        start_time__gte=timezone.localtime(),
    ).select_related("barber")
    return render(request, "main/my_bookings.html", {"bookings": upcoming, "title": "Bronlarim"})
