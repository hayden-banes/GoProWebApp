from django import forms

from controller.models import GoPro


class ConnectForm(forms.ModelForm):
    class Meta:
        model = GoPro
        fields = ["identifier"]
