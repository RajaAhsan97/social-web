from django import forms
from django.contrib.auth.models import User
from .models import Profile

class loginform(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
    

class Register_form(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff"]

    def clean_password2(self):
        pswd1 = self.cleaned_data.get("password")
        pswd2 = self.cleaned_data.get("confirm_password")

        if pswd2 != pswd1:
            raise forms.ValidationError("Password mismatch")
        
        return pswd2

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use')
        return data
    
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id).filter(email=data)
        if qs.exists():
            raise forms.ValidationError('Email alreadyh in use')
        return data
            
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['dob', 'photo']