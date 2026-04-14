from urllib import parse, request

from django.conf import settings


def send_booking_notification(booking):
    if not settings.TELEGRAM_BOT_TOKEN or not booking.barber.telegram_chat_id:
        return False

    message = (
        "Yangi bron so'rovi:\n"
        f"Barber: {booking.barber.full_name}\n"
        f"Mijoz: {booking.client_name}\n"
        f"Telefon: {booking.phone_number}\n"
        f"Vaqt: {booking.start_time:%d.%m.%Y %H:%M}"
    )
    payload = parse.urlencode(
        {
            "chat_id": booking.barber.telegram_chat_id,
            "text": message,
        }
    ).encode()
    try:
        request.urlopen(
            request.Request(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                data=payload,
            ),
            timeout=5,
        )
    except Exception:
        return False
    return True
