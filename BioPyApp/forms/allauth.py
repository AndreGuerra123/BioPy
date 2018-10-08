from django import forms
from django.urls import reverse

from django.utils.translation import ugettext as _

import django.contrib.auth.password_validation as passwordValidation

from BioPyApp.models import User

""" from phonenumber_field.formfields import PhoneNumberField"""
from datetime import date, timedelta
""" from address.forms import AddressField"""
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Column, Row, Div, HTML

#Helpers
def approvedAge(birthdate):
    age = date.today().year - birthdate.year
    return age>=18

def validYears():
   today = date.today()
   return tuple(n for n in range(today.year-100,today.year+1))
""" 
class MyLoginForm(acc_forms.LoginForm):
    username = forms.CharField(label = _('Username'),required=True,max_length=50)
    password = forms.CharField(label = _('Password'),required=True,widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
       super(MyLoginForm, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.form_class = 'form-vertical'
       self.helper.help_text_inline = False
       self.helper.form_method = 'POST'
       self.helper.form_action = reverse('account_login')
       self.helper.form_class = "medium-txt"
       self.helper.form_tag = True
       self.helper.layout = Layout(Row(Field('username'),Field('password'), css_class='col-md-10'))
       self.helper.layout.append(
            HTML(
                "{% if redirect_field_value %}"
                "<input type='hidden' name='{{ redirect_field_name }}'"
                " value='{{ redirect_field_value }}' />"
                "{% endif %}"
            )
       )
       self.helper.layout.append(
            HTML(
                "<p><a class='button' href={url}>{text}</a></p>".format(
                    url=reverse("account_signup"),
                    text=_('New user?')
                )))
       self.helper.layout.append(
            HTML(
                "<p><a class='button' href={url}>{text}</a></p>".format(
                    url=reverse("account_reset_password"),
                    text=_('Forgot password?')
                )))        
       self.helper.add_input(Submit('submit', _('Login'), css_class="btn-success"))

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(email=username).exists():
             raise forms.ValidationError(_("The username does not exist."))
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validators = passwordValidation.get_default_password_validators()
        passwordValidation.validate_password(password=password,password_validators=validators) 
        return password

    def login(self, *args, **kwargs):
        return super(MyLoginForm, self).login(*args, **kwargs)
 """
class MySignUpForm(forms.ModelForm):
    username = forms.CharField(required=True,label="Username",max_length=50,help_text='Required. Inform a valid username.')
    first_name = forms.CharField(required=False,label="First Name",max_length=50,help_text='Inform a valid first name.')
    last_name = forms.CharField(required=False,label="Last Name",max_length=50,help_text='Inform a valid last name.')
    address = AddressField(required=False,help_text='Inform a valid address.')
    email = forms.EmailField(required=True,label="E-mail",max_length=254, help_text='Required. Inform a valid e-mail address.')
    confirm_email = forms.EmailField(required=True,label="Confirm E-mail",max_length=254, help_text='Confirm the previously inserted e-mail address.')
    phone_number = PhoneNumberField(required=False,label="Phone Number",help_text='Inform a valid phone number.')
    birth_date = forms.DateField(required=True,label="Birth Date",help_text='Required. Inform a valid birth date.',widget=forms.SelectDateWidget(years=validYears()))
    terms_conditions = forms.BooleanField(required=True,label="Terms & Conditions",help_text="Required. Confirm agreement with terms and conditions.")
    password = forms.CharField(label="Password",widget=forms.PasswordInput(),help_text='Required. Inform a valid password.')
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(),help_text='Required. Confirm the previously inserted password.')

    class Meta():
        model = User
        fields = ('username', 'first_name', 'last_name',  'address', 'email','confirm_email', 'phone_number','birth_date', 'terms_conditions', 'password', 'confirm_password')


    def __init__(self, *args, **kwargs):
       super(MySignUpForm, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.form_class = 'form-vertical'
       self.helper.help_text_inline = False
       self.helper.form_class = 'medium-txt'
       self.helper.form_tag = False
       self.helper.layout = Layout(Row(
           Fieldset('Basic Information',Field('username'),Field('first_name'),Field('last_name'),css_class='col-md-3'),
           Fieldset('Contact Information', Field('email'),Field('confirm_email'),Field('phone_number'),Field('address'),css_class='col-md-3'),
           Fieldset('Terms & Conditions',Field('birth_date'), Field('terms_conditions'),css_class='col-md-3'),
           Fieldset('Login Information',Field('password'), Field('confirm_password'),css_class='col-md-3')))

    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        if not approvedAge(birth_date):
            raise forms.ValidationError('User must not be underaged.')
        return birth_date

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if not (password == confirm_password):
            raise forms.ValidationError('Password and confirmation must match.')
        return confirm_password

    def clean_confirm_email(self):
        email = self.cleaned_data.get("email")
        confirm_email = self.cleaned_data.get("confirm_email")
        if not (email == confirm_email):
            raise forms.ValidationError('Email and confirmation must match.')
        return confirm_email

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
             raise forms.ValidationError("Email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
             raise forms.ValidationError("Username already exists.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validators = passwordValidation.get_default_password_validators()
        passwordValidation.validate_password(password=password,password_validators=validators) 
        return password

    def clean_terms_conditions(self):
        terms_conditions = self.cleaned_data.get("terms_conditions")
        if not terms_conditions:
            raise forms.ValidationError('New user must agree with terms and conditions.')
        return terms_conditions

    def signup(self, request, user):
        data = self.cleaned_data
        user.email = data.get('email')
        user.username = data.get('username')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.address = data.get('address')
        user.phone_number = data.get('phone_number')
        user.birth_date = data.get('birth_date')
        user.terms_conditions = data.get('terms_conditions')
        user.set_password(data.get('password'))
        user.save()
        return user

""" 
class MyAddEmailForm(acc_forms.AddEmailForm):
    email = forms.EmailField(required=True,label="E-mail",max_length=254, help_text='Required. Inform a valid email address.')
    confirm_email = forms.EmailField(required=True,label="Confirm E-mail",max_length=254, help_text='Required. Confirm the previously inserted email address.')
    
    def __init__(self, *args, **kwargs):
       super(MyAddEmailForm, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
       self.helper.form_class = 'form-vertical'
       self.helper.help_text_inline = False
       self.helper.form_method = 'POST'
       self.helper.form_action = reverse('account_add_email')
       self.helper.form_class = 'medium-txt'
       self.helper.form_tag = True
       self.helper.layout = Layout(Row(Field('email'),Field('confirm_email'), css_class='col-md-10'))
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
             raise forms.ValidationError("Email is already associated to an account.")
        return email

    def clean_confirm_email(self):
        email = self.cleaned_data['email']
        confirm_email = self.cleaned_data['confirm_email']

        if not (email == confirm_email):
            raise forms.ValidationError('E-mails must match.')
        return confirm_email

    def save(self):
        email_address = super(MyAddEmailForm, self).save()
        return email_address

class MyChangePasswordForm(acc_forms.ChangePasswordForm):
    current = forms.CharField(label=_("Current Password"),widget=forms.PasswordInput(),help_text='Required. Inform the current password.')
    password = forms.CharField(label=_("New Password"),widget=forms.PasswordInput(),help_text='Required. Inform a new valid password.')
    confirm = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput(),help_text='Required. Confirm the previously inserted new password.')
    
    def __init__(self, *args, **kwargs):
       super(MyChangePasswordForm, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.form_class = 'form-vertical'
       self.helper.help_text_inline = False
       self.helper.form_method = 'POST'
       self.helper.form_action = reverse('account_change_password')
       self.helper.form_class = 'medium-txt'
       self.helper.form_tag = True
       self.helper.layout = Layout(Row(Field('current'),Field('password'),Field('confirm'), css_class='col-md-10'))
       self.helper.add_input(Submit('submit', _('Change Password'), css_class='btn-success'))

    def clean_current(self):
        current = self.cleaned_data['current']
        if not self.user.check_password(current):
             raise forms.ValidationError("Current password is incorrect.")
        return current

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validators = passwordValidation.get_default_password_validators()
        passwordValidation.validate_password(password=password,password_validators=validators) 
        return password

    def clean_confirm(self):
        password = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm")
        if not approvedConfirmation(password,confirm):
            raise forms.ValidationError(_('New password and confirmation must match.'))
        return confirm
    
    def save(self):
        super(MyChangePasswordForm, self).save()
        self.user.set_password(self.cleaned_data.get("password"))
        self.user.save()

class MySetPassword(acc_forms.SetPasswordForm):
    password = forms.CharField(label="New Password",widget=forms.PasswordInput(),help_text='Required. Inform a new valid password.')
    confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(),help_text='Required. Confirm the previously inserted new password.')

    def __init__(self, *args, **kwargs):
       super(MySetPassword, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.add_input(Submit('submit', 'Set Password', css_class='btn-success'))
       self.helper.form_class = 'form-vertical'
       self.helper.help_text_inline = False
       self.helper.form_method = 'POST'
       self.helper.form_action = reverse('account_set_password')
       self.helper.form_class = 'medium-txt'
       self.helper.form_tag = True
       self.helper.layout = Layout(Row(Field('password'),Field('confirm'), css_class='col-md-10'))

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validators = passwordValidation.get_default_password_validators()
        passwordValidation.validate_password(password=password,password_validators=validators) 
        return password

    def clean_confirm(self):
        password = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm")
        if not approvedConfirmation(password,confirm):
            raise forms.ValidationError('New password and confirmation must match.')
        return confirm

    def save(self):
        super(MySetPasswordForm, self).save()
        self.user.set_password(self.cleaned_data.get("password"))
        self.user.save()

class MyResetPasswordForm(acc_forms.ResetPasswordForm):
    email = forms.EmailField(required=True,label="E-mail",max_length=254, help_text='Required. Inform a valid email address.')

    def __init__(self, *args, **kwargs):
       super(MyResetPasswordForm, self).__init__(*args, **kwargs)
       self.helper = FormHelper()
       self.helper.form_class = 'form-vertical'
       self.helper.help_text_inline = False
       self.helper.form_method = 'POST'
       self.helper.form_action = reverse('account_reset_password')
       self.helper.form_class = 'medium-txt'
       self.helper.form_tag = True
       self.helper.layout = Layout(Row(Field('email'), css_class='col-md-10'))
       self.helper.add_input(Submit('submit', _('Reset Password'), css_class='btn-success'))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
             raise forms.ValidationError(_("Email does not have an account associated."))
        return email

    def save(self):
        super(MyResetPasswordForm, self).save()
        return self.cleaned_data['email']
        
class MyResetPasswordKeyForm(acc_forms.ResetPasswordKeyForm): #TODO:
    
    def save(self):

        # Add your own processing here.

        # Ensure you call the parent classes save
        # .save() does not return anything
        super(MyResetPasswordKeyForm, self).save()
 """