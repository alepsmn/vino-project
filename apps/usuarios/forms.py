from django import forms
from django.contrib.auth.models import User
from .models import PerfilCliente

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