# TrimTime

Django orqali qurilgan, barbershop uchun navbat va bron sayti.

## Ishga tushirish

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_barbers
python manage.py runserver
```

Admin panel: `http://127.0.0.1:8000/admin/`

## Telegram xabarnoma

`TELEGRAM_BOT_TOKEN` environment variable ni o'rnating va admin panelda barber uchun `telegram_chat_id` kiriting.

## Foydalanuvchi sahifalari

- Home: barberlar ro'yxati
- Barber detail: 1 haftalik auto slotlar
- Bronlarim: foydalanuvchi joriy bronlari
- Borib kelinganlar: completed holatdagi bronlar
