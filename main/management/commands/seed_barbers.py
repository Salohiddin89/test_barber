from django.core.management.base import BaseCommand

from main.models import Barber


class Command(BaseCommand):
    help = "Demo barber yozuvlarini yaratadi"

    def handle(self, *args, **options):
        samples = [
            {
                "shop_name": "Downtown Fade Studio",
                "first_name": "Javohir",
                "last_name": "Sattorov",
                "years_experience": 6,
                "specialty": "Skin fade va beard design",
                "bio": "Aniq kontur, zamonaviy fade va premium xizmat ko'rsatishga ixtisoslashgan barber.",
                "image_url": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=900&q=80",
            },
            {
                "shop_name": "Kings Cut Lounge",
                "first_name": "Bekzod",
                "last_name": "Tursunov",
                "years_experience": 8,
                "specialty": "Classic cut va hot towel shave",
                "bio": "Klassik uslubni zamonaviy ko'rinish bilan birlashtiradigan tajribali usta.",
                "image_url": "https://images.unsplash.com/photo-1512690459411-b0fdacec10fd?auto=format&fit=crop&w=900&q=80",
            },
        ]
        created = 0
        for data in samples:
            _, was_created = Barber.objects.get_or_create(
                shop_name=data["shop_name"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} ta demo barber qo'shildi."))
