from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone

from .models import Barber, Booking


class BookingFlowTests(TestCase):
    def setUp(self):
        self.barber = Barber.objects.create(
            shop_name="Trim House",
            first_name="Jamshid",
            last_name="Karimov",
            years_experience=5,
            specialty="Fade va classic cut",
            bio="Professional barber",
        )

    def test_week_slots_generated(self):
        slots = self.barber.get_week_slots()
        self.assertEqual(len(slots), 7)
        self.assertTrue(any(day["slots"] for day in slots))

    def test_pending_requests_can_share_same_slot_until_acceptance(self):
        slot = timezone.make_aware(datetime(2099, 1, 1, 10, 0))
        Booking.objects.create(
            barber=self.barber,
            client_name="Ali",
            phone_number="+998901234567",
            start_time=slot,
            session_key="abc",
        )
        second = Booking.objects.create(
            barber=self.barber,
            client_name="Vali",
            phone_number="+998901111111",
            start_time=slot,
            session_key="xyz",
        )
        self.assertEqual(second.status, Booking.Status.PENDING)

    def test_only_accepted_bookings_block_slots(self):
        tomorrow = timezone.localtime() + timedelta(days=1)
        slot = timezone.make_aware(
            datetime.combine(
                tomorrow.date(),
                datetime.strptime("11:00", "%H:%M").time(),
            )
        )
        Booking.objects.create(
            barber=self.barber,
            client_name="Ali",
            phone_number="+998901234567",
            start_time=slot,
            session_key="abc",
            status=Booking.Status.ACCEPTED,
        )
        taken_slots = {
            item["start"]
            for day in self.barber.get_week_slots()
            for item in day["slots"]
            if item["is_taken"]
        }
        self.assertIn(slot, taken_slots)

    def test_booking_gets_approval_token(self):
        slot = timezone.make_aware(datetime(2099, 1, 1, 10, 0))
        booking = Booking.objects.create(
            barber=self.barber,
            client_name="Ali",
            phone_number="+998901234567",
            start_time=slot,
            session_key="abc",
        )
        self.assertTrue(booking.approval_token)
