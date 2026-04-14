from datetime import datetime, timedelta
import secrets

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Barber(models.Model):
    shop_name = models.CharField(max_length=120, verbose_name="Barbershop nomi")
    first_name = models.CharField(max_length=80, verbose_name="Ism")
    last_name = models.CharField(max_length=80, verbose_name="Familiya")
    years_experience = models.PositiveIntegerField(default=1, verbose_name="Staj (yil)")
    specialty = models.CharField(max_length=180, verbose_name="Yo'nalish")
    bio = models.TextField(verbose_name="Qisqacha ma'lumot")
    image_url = models.URLField(blank=True, verbose_name="Rasm URL")
    work_start = models.TimeField(default=datetime.strptime("08:00", "%H:%M").time(), verbose_name="Ish boshlanishi")
    work_end = models.TimeField(default=datetime.strptime("19:00", "%H:%M").time(), verbose_name="Ish tugashi")
    slot_minutes = models.PositiveIntegerField(default=60, verbose_name="Har slot davomiyligi")
    telegram_chat_id = models.CharField(max_length=64, blank=True, verbose_name="Telegram chat ID")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Barber"
        verbose_name_plural = "Barberlar"

    def __str__(self):
        return f"{self.shop_name} - {self.full_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("barber_detail", args=[self.pk])

    def clean(self):
        if self.work_start >= self.work_end:
            raise ValidationError("Ish boshlanishi tugash vaqtidan oldin bo'lishi kerak.")

    def get_week_slots(self):
        now = timezone.localtime()
        taken = {
            booking.start_time
            for booking in self.bookings.filter(
                status__in=[Booking.Status.ACCEPTED, Booking.Status.COMPLETED]
            )
            if booking.start_time >= now
        }
        slots_by_day = []
        for day_offset in range(7):
            current_day = (now + timedelta(days=day_offset)).date()
            current_dt = timezone.make_aware(datetime.combine(current_day, self.work_start))
            end_dt = timezone.make_aware(datetime.combine(current_day, self.work_end))
            daily_slots = []
            while current_dt + timedelta(minutes=self.slot_minutes) <= end_dt:
                if current_dt > now:
                    daily_slots.append(
                        {
                            "start": current_dt,
                            "is_taken": current_dt in taken,
                        }
                    )
                current_dt += timedelta(minutes=self.slot_minutes)
            slots_by_day.append(
                {
                    "date": current_day,
                    "label": current_day.strftime("%d %b"),
                    "weekday": current_day.strftime("%A"),
                    "slots": daily_slots,
                }
            )
        return slots_by_day


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        ACCEPTED = "accepted", "Qabul qilindi"
        COMPLETED = "completed", "Borib kelindi"
        CANCELLED = "cancelled", "Bekor qilindi"

    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name="bookings")
    client_name = models.CharField(max_length=120, verbose_name="Mijoz ismi")
    phone_number = models.CharField(max_length=32, verbose_name="Telefon raqam")
    start_time = models.DateTimeField(verbose_name="Bron vaqti")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    session_key = models.CharField(max_length=64, db_index=True)
    approval_token = models.CharField(max_length=64, unique=True, editable=False, blank=True)
    notes = models.CharField(max_length=255, blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time", "-created_at"]
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"

    def __str__(self):
        return f"{self.client_name} - {self.barber.full_name} ({self.start_time:%d.%m %H:%M})"

    @property
    def is_past(self):
        return self.start_time < timezone.localtime()

    def save(self, *args, **kwargs):
        if not self.approval_token:
            self.approval_token = secrets.token_urlsafe(24)
        super().save(*args, **kwargs)
