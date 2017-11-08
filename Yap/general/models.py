# default Imports
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# the following is what allows user to save the state using the state field
from django_localflavor_us.models import USStateField

#--------------------------------
# the following are tables realted to the app and general information
#--------------------------------

# Profile saves every users profile information
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # server
    first_name = models.CharField(max_length=25, default='first')
    last_name = models.CharField(max_length=25, default='last')
    bio = models.CharField(max_length=220, default='bio')
    dob = models.DateField(default='1950-01-01')
    street = models.CharField(max_length=200, default='street address')
    city = models.CharField(max_length=100, default='city')
    state = USStateField(default='CA')
    zip_code = models.IntegerField(default=12345)
    phone = models.BigIntegerField(default=0)  # user
    balance = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    dwolla_id = models.CharField(max_length=200, default='https://api-sandbox.dwolla.com')
    synapse_id = models.CharField(max_length=200, default='123456789')
    created = models.DateTimeField(auto_now_add=True)  # server

# Privacy sotres every users different privacy settings for viewing profiles
class Privacy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.SmallIntegerField(default=1)
    # 1 = everyone
    # 2 = friends
    # 3 = me
    friends = models.SmallIntegerField(default=1)
    # 1 = everyone
    # 2 = friends
    # 3 = me
    expenses = models.SmallIntegerField(default=1)
    # 1 = everyone
    # 2 = friends
    # 3 = me
    searchable = models.SmallIntegerField(default=1)
    # 1 = everyone
    # 2 = friends
    # 3 = me

# Request will store all of the friend request that are sent between two users
class Request(models.Model):
    user = models.CharField(max_length=22, default='current user')
    requested = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

# Friend will store all of the friendships that have been created
class Friend(models.Model):
    user = models.CharField(max_length=22, default='current user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    category = models.SmallIntegerField(default=1)
    # 1 = standard/default
    # 2 = favorite
    # 3 = family
    created = models.DateTimeField(auto_now_add=True)

# Group will store all of the groups info that is created in the app
class Group(models.Model):
    name = models.CharField(max_length = 25)
    description = models.CharField(max_length = 250, null=True)
    location = models.CharField(max_length = 40, null=True)
    count = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    # 1 = active
    # 2 = inactive
    # 3 = suspended
    reference_code = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

# Member stores all of the different members to each of the created groups
class Member(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE) #user
    group = models.ForeignKey(Group, default=1 , on_delete=models.CASCADE) #user
    status = models.SmallIntegerField(default=1) #user
    # 1 = member
    # 2 - host
    funding = models.DecimalField(decimal_places=2, max_digits=9, default=0.00)
    created = models.DateTimeField(auto_now_add=True) #server

# Expense will store all of the expense that are created (both single and group)
# will be used as the foundation for money transaction transfers though the app
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    description = models.CharField(max_length=200, default = 'expense')
    name = models.CharField(max_length=100, default = 'group name')
    location = models.CharField(max_length=100, default = 'location')
    status = models.SmallIntegerField(default = 1)
    # 1 = unpaid
    # 2 = paid
    split = models.SmallIntegerField(default = 1)
    # 1 = even
    # 2 = idividual
    reference = models.IntegerField(default = '101', null = True)
    # reference is assigned for single transaction for tracking purposes
    created_by = models.CharField(max_length = 200, default = 'username', null=True)
    created = models.DateTimeField(auto_now_add=True)

# Checklist stores the overall infomraiton about each Checklist
class Checklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='checklist')
    total = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    # total amount required from each person
    created = models.DateTimeField(auto_now_add=True)

# Item saves all of the individal items that make a Checklist
class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)
    item = models.CharField(max_length=100, default='item')
    amount = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    created = models.DateTimeField(auto_now_add=True)

# User Acitivity stores all of the activity info that are directly realted to a
#   specific user
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.CharField(max_length=150, null=True)
    expense = models.ForeignKey(Expense, null=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, default='some action')
    accepted = models.SmallIntegerField(default = 1)
    # 1 = yes
    # 2 = no
    status = models.SmallIntegerField(default=1)
    # 1 = unseen
    # 2 = seen
    reference = models.IntegerField(default = '101', null = True)
    validation = models.SmallIntegerField(default = 1)
    # 1 = no validation required
    # 2 = validation required
    created = models.DateTimeField(auto_now_add=True)

# Group Activity stores all of the actiivty related to a group that was create
class GroupActivity(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    host = models.CharField(max_length=100, null=True)
    expense = models.ForeignKey(Expense, null=True, on_delete=models.CASCADE)
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=200, default='some action')
    general = models.SmallIntegerField(default = 1)
    # 1 = general
    # 2 = logged in user
    validation = models.SmallIntegerField(default = 1)
    # 1 = no validation required
    # 2 = validation required
    accepted = models.SmallIntegerField(default = 1)
    # 1 = yes
    # 2 = no
    created = models.DateTimeField(auto_now_add=True)

#------------------------------------
# The following are realted to the Synapse Api & local infomraiton
#------------------------------------

# Synapse Accounts locally stores a users linked accounts through login or an/rn
class SynapseAccounts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Bank Account')
    account_id = models.CharField(max_length=100, default='00000')
    account_class = models.CharField(max_length=50, default='Checking')
    bank_name = models.CharField(max_length=150, default='DefaultBank')
    balance = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    main = models.IntegerField(default=1)
    # 1 = standard
    # 2 = default
    create = models.DateTimeField(auto_now_add=True)
