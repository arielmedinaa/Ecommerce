from django import forms

class MigracionProducto(forms.Form):
    file = forms.FileField(required=True)