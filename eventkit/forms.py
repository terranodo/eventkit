from django import forms


class RegisterVoyager(forms.Form):
    voyager_base_url = forms.CharField(label='Voyager Base URL', required=True)

