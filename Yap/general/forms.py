# default django imports for the formset_factory
from django import forms
from django.forms import ModelForm, extras
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# all model imports related to this project
from .models import Profile, Privacy, Request, Friend, Group, Member, Expense, Checklist, Item, UserActivity, GroupActivity, SynapseAccounts

#--------------------------------------------
# the following are general forms used though the applicaiton
#--------------------------------------------

# form used to login to accounts
class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)

# form used to signup into your accounts
class SignupForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=16, widget=forms.PasswordInput)
    verify = forms.CharField(max_length=16, widget=forms.PasswordInput)
    email = forms.EmailField(max_length=40)

# form used to setup the users profiles
class ProfileForm(forms.ModelForm):
    split_choices = (('1', 'public'),
                     ('2', 'private'))
    privacy = forms.TypedChoiceField(
        choices=split_choices, widget=forms.RadioSelect, coerce=int
    )
    dob = forms.DateField(widget=forms.widgets.DateInput(attrs={'type':'date'}))
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'dob', 'street', 'city', 'state',
                    'zip_code', 'phone', 'privacy']

# form for creating a new group
class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'location', 'description']

# the form for updating users accounts
class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

# the form allows the user to update public information
class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20, label="First Name")
    last_name = forms.CharField(max_length=20, label="Last Name")
    class Meta:
        model = Profile
        fields = ['bio', 'first_name', 'last_name']

# the following will allow user to update his profile infomraiton
class InfoUpdateForm(forms.ModelForm):
    dob = forms.DateField(widget=forms.widgets.DateInput(attrs={'type':'date'}))
    class Meta:
        model = Profile
        fields = ['phone', 'dob', 'street', 'city', 'state', 'zip_code']

# the form that will update the users Password
class PasswordUpdateForm(forms.Form):
    current_password = forms.CharField(max_length=20, label="Current password", widget=forms.PasswordInput)
    new_password = forms.CharField(max_length=20, label="New password", widget=forms.PasswordInput)
    verify_password = forms.CharField(max_length=20, label="Verify password", widget=forms.PasswordInput)

# the form is going to be used to update the users privacy settings
class PrivacyUpdateForm(forms.ModelForm):
    privacy_choices = (('1', 'Everyone'),
                       ('2', 'Friends'),
                       ('3', 'Only Me'))
    friends = forms.TypedChoiceField(
        label="Friends", choices=privacy_choices
    )
    groups = forms.TypedChoiceField(
        label="Friends", choices=privacy_choices
    )
    expenses = forms.TypedChoiceField(
        label="Friends", choices=privacy_choices
    )
    searchable = forms.TypedChoiceField(
        label="Friends", choices=privacy_choices
    )
    class Meta:
        model = Privacy
        fields = ['friends', 'groups', 'expenses', 'searchable']

# this form is used to create an expenses
class CreateExpenseForm(forms.ModelForm):
    split_choices = (('1', 'even'),
                      ('2', 'individual'))
    split = forms.TypedChoiceField(
        choices=split_choices, widget=forms.RadioSelect, coerce=int
    )
    class Meta:
        model = Expense
        fields = ['name', 'location', 'split']

# the form which updates the expense with new information
class UpdateExpenseEvenForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount']

# the following form is going to be used to updated the expense individually which
# is different than the standard Update
class UpdateExpenseIndividualForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description']

# this form is a custom form that is used to create a checklist, will be changed to
# dynamic adaptation
class CreateChecklistForm(forms.ModelForm):
    item1 = forms.CharField(max_length=50, label='Item')
    item2 = forms.CharField(max_length=50, label='Item')
    item3 = forms.CharField(max_length=50, label='Item')
    amount1 = forms.DecimalField(decimal_places=2, max_digits=9, label='Amount')
    amount2 = forms.IntegerField(label='Amount')
    amount3 = forms.IntegerField(label='Amount')
    class Meta:
        model = Checklist
        fields = ['name', 'item1', 'amount1', 'item2', 'amount2', 'item3', 'amount3']

#--------------------------------------------
# the following forms are for Synapse API and linking bank accounts iwth application
#---------------------------------------------

# allows user to link bank accounts through bank login
class SynapseAccountForm(forms.Form):
    type_choices = (('PERSONAL', 'PERSONAL'),
                    ('BUSINESS', 'BUSINESS'))
    class_choices = (('CHECKING', 'CHECKING'),
                       ('SAVINGS', 'SAVINGS'))
    accountName = forms.CharField(
        max_length=100, label="Account Name"
    )
    routingNumber = forms.CharField(max_length=22, label="Routing Number")
    accountNumber = forms.CharField(max_length=22, label="Account Number")
    account_class = forms.TypedChoiceField(
        choices = class_choices,
        label = 'Class'
    )
    account_type = forms.TypedChoiceField(
        choices = type_choices,
        label = 'Type'
    )

# allows user to link bank accounts through account number and routing Number
class synapseLoginForm(forms.Form):
    bank_code_choices = (('ally', 'Ally Bank'),
                         ('arvest', 'Associated Bank'),
                         ('bofa', 'Bank of America'),
                         ('boftw', 'Bank of the West'),
                         ('capone', 'Capital One'),
                         ('capone360', 'Capital One 360'),
                         ('chase', 'Chase'),
                         ('citi', 'Citibank'),
                         ('citizens', 'Citizens Bank'),
                         ('fidelity', 'Fidelity'),
                         ('firsthawaiian', 'First Hawaiian Bank'),
                         ('gobank', 'GoBank'),
                         ('hsbc', 'HSBC Bank'),
                         ('mtb', 'M&T Bank'),
                         ('nfcu', 'Navy Federal Credit Union'),
                         ('svb', 'Silicon Valley Bank'),
                         ('synchrony', 'Synchrony Bank'),
                         ('td', 'TD Bank'),
                         ('union', 'Union Bank'),
                         ('us', 'US Bank'),
                         ('usaa', 'USAA'),
                         ('wells', 'Wells Fargo'))
    bank_code = forms.TypedChoiceField(choices=bank_code_choices)
    bank_id = forms.CharField(max_length=100, label="Bank Username")
    bank_password = forms.CharField(max_length=100, widget=forms.PasswordInput(), label="Bank Password")
