from django import forms
from django.contrib.auth.models import User
from datetime import date
from .models import PerfilCliente


class RegistroForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    dni = forms.CharField(max_length=20)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    telefono = forms.CharField(max_length=20, required=False)
    direccion = forms.CharField(max_length=255, required=False)
    ciudad = forms.CharField(max_length=100, required=False)
    codigo_postal = forms.CharField(max_length=10, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data["fecha_nacimiento"]
        hoy = date.today()
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        if edad < 18:
            raise forms.ValidationError("Debes ser mayor de 18 años.")
        return fecha

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"]
        )

        PerfilCliente.objects.create(
            user=user,
            dni=self.cleaned_data["dni"],
            fecha_nacimiento=self.cleaned_data["fecha_nacimiento"],
            telefono=self.cleaned_data.get("telefono"),
            direccion=self.cleaned_data.get("direccion"),
            ciudad=self.cleaned_data.get("ciudad"),
            codigo_postal=self.cleaned_data.get("codigo_postal"),
            pais="España"
        )

        return user


class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = PerfilCliente
        fields = [
            'dni', 'fecha_nacimiento', 'telefono', 'direccion',
            'ciudad', 'codigo_postal', 'pais'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if not fecha:
            raise forms.ValidationError("Debes indicar tu fecha de nacimiento.")
        hoy = date.today()
        edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
        if edad < 18:
            raise forms.ValidationError("Debes ser mayor de 18 años.")
        return fecha
