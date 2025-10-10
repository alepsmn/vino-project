from django import forms
from django.contrib.auth.models import User
from .models import PerfilCliente
from datetime import date

class RegistroForm(forms.ModelForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = PerfilCliente
        fields = ['telefono', 'direccion', 'ciudad', 'codigo_postal']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        perfil = PerfilCliente(
            user=user,
            telefono=self.cleaned_data.get('telefono'),
            direccion=self.cleaned_data.get('direccion'),
            ciudad=self.cleaned_data.get('ciudad'),
            codigo_postal=self.cleaned_data.get('codigo_postal')
        )
        if commit:
            user.save()
            perfil.save()
        return user

class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = PerfilCliente
        fields = ['dni', 'fecha_nacimiento', 'telefono', 'direccion', 'ciudad', 'codigo_postal', 'pais']
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