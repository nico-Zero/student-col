from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class GenerateWhiteboardForm(forms.Form):
    pass

class DeleteCurrentWhiteboardForm(forms.Form):
    pass

class LoginForm(forms.Form):
    username = forms.CharField(max_length=120)
    password = forms.CharField(max_length=16, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields = ('username','email' ,'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["about"]

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        instance = super(EditProfileForm, self).save(commit=False, *args, **kwargs)
        return instance.save() if commit else instance