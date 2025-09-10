from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import User, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    school_name = forms.CharField(max_length=200, required=False)
    school_type = forms.ChoiceField(choices=User.SCHOOL_TYPES, required=False)
    grade_level = forms.CharField(max_length=50, required=False)
    city = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'school_name', 
                 'school_type', 'grade_level', 'city', 'country')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('school_name', css_class='form-group col-md-6 mb-0'),
                Column('school_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('grade_level', css_class='form-group col-md-4 mb-0'),
                Column('city', css_class='form-group col-md-4 mb-0'),
                Column('country', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Join EcoLearning!', css_class='btn btn-success btn-lg')
        )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar', 
                 'school_name', 'school_type', 'grade_level', 'city', 'country',
                 'notifications_enabled', 'public_profile']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            'bio',
            'avatar',
            Row(
                Column('school_name', css_class='form-group col-md-6 mb-0'),
                Column('school_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('grade_level', css_class='form-group col-md-4 mb-0'),
                Column('city', css_class='form-group col-md-4 mb-0'),
                Column('country', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('notifications_enabled', css_class='form-group col-md-6 mb-0'),
                Column('public_profile', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )
