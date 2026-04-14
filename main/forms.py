from django import forms


class BookingCreateForm(forms.Form):
    client_name = forms.CharField(
        max_length=120,
        label="Ism familiyangiz",
        widget=forms.TextInput(attrs={"placeholder": "Masalan, Ali Valiyev"}),
    )
    phone_number = forms.CharField(
        max_length=32,
        label="Telefon raqamingiz",
        widget=forms.TextInput(attrs={"placeholder": "+998 90 123 45 67"}),
    )
