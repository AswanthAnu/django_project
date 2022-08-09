from django import forms
from .models import Account

# adding form to html

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Password', 'id' :'password_id', 'class':'form-control',
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password', 'id' :'confirm_password_id', 'class':'form-control',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

        widgets = {
            'first_name' : forms.TextInput(attrs={'id' : 'first_name_id'}),
            'last_name' : forms.TextInput(attrs={'id' : 'last_name_id'}),
            'phone_number' : forms.TextInput (attrs={'id' : 'phone_number_id'}),
            'email' : forms.EmailInput (attrs={'id' : 'email_id'}),
            'password' : forms.PasswordInput (attrs={'id' : 'password_id'}),
        }

  
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Password does not match'
            )

    # overriding to add place_holder and style

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Email Address'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        

