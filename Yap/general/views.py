# the following are defauly django imports that are needed
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import formset_factory
from django.db.models import Q

# imports from project files connected thought the files
from .models import *
from .forms import *

# utility imports for this project
import os, requests, json
from random import randint
from decimal import Decimal

# synapse import statements that are needed
from synapse_pay_rest import Client, Node, Transaction
from synapse_pay_rest import User as SynapseUser
from synapse_pay_rest.models.nodes import AchUsNode

#----------- DEFAULT TEST LINK ---------------------------------------
def Test(request):
    return render(request, 'content///test.html')

#---------- SYNAPSE API INITIALIZATION -------------------------------
# the following are all of the different credentials that are needed in order to
# initiate the connect between the api and opentab
APP_CLIENT_ID = 'client_id_SOJMCFkagKAtvTpem0ZWPRbwznQ2yc5h0dN6YiBl'
APP_CLIENT_SECRET = 'client_secret_muUbizcGBq2oXKQTMEphg0S4tOyH5xLYNsPkC3IF'
APP_FINGERPRINT = '599378e9a63ec2002d7dd48b'
APP_IP_ADRESS = '127.0.0.1'

# the following are going to be all of the different credentials that are going
# to be needed in order to establish connection
args = {
    'client_id':APP_CLIENT_ID,
    'client_secret':APP_CLIENT_SECRET,
    'fingerprint':APP_FINGERPRINT,
    'ip_address':APP_IP_ADRESS,
    'development_mode':True,
    'logging':False,
}

# this is the call that takes the credentials and sends the connect request to
# validate credentials
client = Client(**args)

#---------- YAP SPECIFIC VIEWS --------------------------------------
#---------- SETTING UP ACCOUNT --------------------------------------
# new user signup
def signup(request):
    # the following will determine if the form is submitted or not
    if request.method == 'POST':
        form = SignupForm(request.POST)
        # the following section validates the entire form and processed the data
        if form.is_valid():
            # the following will make sure the data is clean and then store them
            # into new variables
            cd = form.cleaned_data
            username = cd['username']
            password = cd['password']
            verify = cd['verify']
            email = cd['email']
            # the folloiwng will make sure the password and verification are matching
            # before storing the info into the database
            if password == verify:
                # the following will hash the password
                secure_password = make_password(password)
                new_user = User.objects.create(
                    username = username,
                    password = secure_password,
                    email = email,
                )
                # the following will store the username of the account that was just
                # created in to the session so that the app can track the user that
                # is logged in
                request.session['username'] = username
                return redirect('profile_setup')
            else:
                # if password and verification dont match, a message will be sent
                # back to the user so they can fill in the correct info.
                message = 'Password and Verify dont match'
                parameters = {
                    'form':form,
                    'message':message,
                }
                return render(request, 'content/signup.html', parameters)
    else:
        # this will display the form if it waas not submmited.
        form = SignupForm()
        message = 'Fill out the form'
        parameters = {
            'form':form,
            'message':message,
        }
        return render(request, 'content/signup.html', parameters)

# users profile setup - initial
def profileSetup(request):
    if 'username' not in request.session:
        return redirect('login')
    else:
        # the following is just going to grab the currently logged in user and
        # save the profile information to the appropriate user
        username = request.session['username']
        currentUser = User.objects.get(username = username)
        # the following is the provessing for the form where the user entered
        # the profile informaiton
        if request.method == 'POST':
            form = ProfileForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                # storing all of the informaiton from the form
                first_name = cd['first_name']
                last_name = cd['last_name']
                dob = cd['dob']
                city = cd['city']
                state = cd['state']
                phone = cd['phone']
                # this is the new record that is going to be created and saved
                new_profile = Profile.objects.create(
                    user = currentUser,
                    first_name = first_name,
                    last_name = last_name,
                    dob = dob,
                    city = city,
                    state = state,
                    phone = phone,
                )
                # the follownig is gong to be the activity for setting up a profile_setup
                description = 'Welcome ' + currentUser.username + ', you have created your new Yap profile'
                profile_activity = UserActivity.objects.create(
                    user = currentUser,
                    description = description,
                    status = 1
                )
                # createUserDwolla(request, ssn)
                createUserSynapse(request)
                return redirect('user_groups')
        else:
            # this is what is going to be saved into the html file and used to
            # render the file
            form = ProfileForm()
            message = 'fill out form below'
            parameters = {
                'form':form,
                'currentUser':currentUser,
                'message':message,
            }
            return render(request, 'content/profile_setup.html', parameters)

# users login
def loginPage(request):
    # the following will check to see if the form is submitted or not.
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # the following validates the form and will store the cleaned data that the
        # user submitted.
        if form.is_valid():
            cd = form.cleaned_data
            username = cd['username']
            password = cd['password']
            # the following line will authenticate the user based on the username
            # and password that was submiited.
            user = authenticate(username=username, password=password)
            # if the user ;is authentic, the username will be stored in the session
            # and redirect the user to their home page.
            if user:
                request.session['username'] = username
                profiles = Profile.objects.all()
                for profile in profiles:
                    if profile.user.username == user.username:
                        return redirect('user_groups')
            else:
                # if the user is not authentic, a error message will be displayed
                # and the user will have to re login
                message = 'invalid login info'
                parameters = {
                    'message':message,
                    'form':form,
                }
            return render(request, 'content/login.html', parameters)
    else:
        # this will display the login form if it was not submitted initially
        form = LoginForm()
        message = 'Login Below'
        parameters = {
            'form':form,
            'message':message,
        }
        return render(request, 'content/login.html', parameters)

#------------- USERS HOME PAGE ------------------------------------------
# users home page - logged in users page
def userHome(request):
    # grabs the currently logged in user and his profile
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # grabs all users activities for profile page
    activities = UserActivity.objects.filter(user = currentUser).all()
    # tracks how many of them have not been seen yet
    unseen_activity = UserActivity.objects.filter(user = currentUser).filter(status=1).filter(account=None).count()
    # grabs all of the freind require that they user has sent or received
    requester = Request.objects.filter(user = currentUser.username).all()
    requested = Request.objects.filter(requested = currentUser).all()
    # combination of both request queries above
    requests = requester | requested
    # grabs all the logged in users friends
    friender = Friend.objects.filter(user = currentUser.username).all()
    friended = Friend.objects.filter(friend = currentUser).all()
    # combination of the two queries above
    friends = friender | friended
    # everything that needs to be passed to the tempalte
    parameters = {
        'currentUser':currentUser,
        'activities':activities,
        'unseen_activity':unseen_activity,
        'requests':requests,
        'friends':friends
    }

    return render(request, 'content/user_home.html', parameters)

# search for user by username
def searchedUser(request):
    # grabs the logged in users profile and account
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # all of the apps users to check if the searched user exists in the database
    users = User.objects.all()
    # check if form is submitted or needs to be displayed
    if request.method == 'POST':
        # the username that was searched
        searched = request.POST['searched']
        # go through the users and check to see if the current user exists
        for user in users:
            if user.username == searched:
                searchedUser = user
                # display users profile if user exists
                return redirect('user_profile', userName = searchedUser.username)
        # goes home if doesnt exist
        return redirect('user_groups')

# searched users profile
def userProfile(request, userName):
    # grabs the logged in user account and profiel
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # initialize two variabel to test for later
    viewedUser = None
    viewedProfile = None
    # grab all users and check to see if the user has a profile
    users = User.objects.all()
    for user in users:
        if user.username == userName:
            viewedUser = user
            viewedProfile = Profile.objects.get(user = viewedUser)
    # if there is a user, it will check to see if the user is a friend to determine
    # whether or not a friend request tab should be presented
    if viewedUser != None:
        friends = Friend.objects.filter(Q(user = currentUser.username, friend = viewedUser) | Q(user = viewedUser.username, friend = currentUser))
    # parameters that need to be passed to template
    parameters = {
        'currentUser':currentUser,
        'currentProfile':currentProfile,
        'viewedUser':viewedUser,
        'viewedProfile':viewedProfile,
        'friends':friends
    }
    # render the users profile template
    return render(request, 'content/user_profile.html', parameters)

def userSettings(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # commented during initial testing because of dumplcate objects
    #currentPrivacy = Privacy.objects.get(user = currentUser)
    currentPrivacy = Privacy.objects.filter(user = currentUser).first()
    passwordMessage = ''
    if request.method == "POST":
        if 'userSubmit' in request.POST:
            updateUserOne = AccountUpdateForm(request.POST)
            if updateUserOne.is_valid():
                cd = updateUserOne.cleaned_data
                username = cd['username']
                email = cd['email']
            updateUserTwo = UserUpdateForm(request.POST)
            if updateUserTwo.is_valid():
                cd = updateUserTwo.cleaned_data
                first_name = cd['first_name']
                last_name = cd['last_name']
                bio = cd['bio']
                # the following is going to update the appropriate records in the
                # table with the updated correct informaiton
                update_user = currentUser
                update_user.username = username
                update_user.email = email
                update_user.save()
                update_profile = currentProfile
                update_profile.first_name = first_name
                update_profile.last_name = last_name
                update_profile.bio = bio
                update_profile.save()
                updateSessionUsername(request, update_user.username)

                # new activity for updating your profile
                description = 'You have updated your user profile'
                user_profile_update = UserActivity.objects.create(
                    user = currentUser,
                    description = description,
                    status = 1
                )

                return redirect('home_page')
        if 'passwordSubmit' in request.POST:
            updatePassword = PasswordUpdateForm(request.POST)
            if updatePassword.is_valid():
                cd = updatePassword.cleaned_data
                current_password = cd['current_password']
                new_password = cd['new_password']
                verify_password = cd['verify_password']
                user = authenticate(username=currentUser.username, password=current_password)
                if user:
                    if new_password == verify_password:
                        secured_password = make_password(new_password)
                        update_user = currentUser
                        update_user.password = secured_password
                        update_user.save()

                        # new activity for updating your profile
                        description = 'You have updated your password'
                        user_profile_update = UserActivity.objects.create(
                            user = currentUser,
                            description = description,
                            status = 1
                        )

                        return redirect('home_page')
                    else:
                        passwordMessage = 'The two passwords do not match'
                        # if the passwords do no match
                else:
                    passwordMessage = 'Current password does not match our records'
                    # in case the old password is not what is saved in the database
        if 'infoSubmit' in request.POST:
            updateInfo = InfoUpdateForm(request.POST)
            if updateInfo.is_valid():
                cd = updateInfo.cleaned_data
                phone = cd['phone']
                dob = cd['dob']
                street = cd['street']
                city = cd['city']
                state = cd['state']
                zip_code = cd['zip_code']
                update_profile = currentProfile
                update_profile.phone = phone
                update_profile.dob = dob
                update_profile.street = street
                update_profile.city = city
                update_profile.state = state
                update_profile.zip_code = zip_code
                update_profile.save()

                # new activity for updating your profile
                description = 'You have updated your profile info'
                user_profile_update = UserActivity.objects.create(
                    user = currentUser,
                    description = description,
                    status = 1
                )

                return redirect('home_page')
        if 'privacySubmit' in request.POST:
            updatePrivacy = PrivacyUpdateForm(request.POST)
            if updatePrivacy.is_valid():
                cd = updatePrivacy.cleaned_data
                groups = cd['groups']
                friends = cd['friends']
                expenses = cd['expenses']
                searchable = cd['searchable']
                update_privacy = currentPrivacy
                update_privacy.groups = groups
                update_privacy.friends = friends
                update_privacy.expenses = expenses
                update_privacy.searchable = searchable
                update_privacy.save()

                # new activity for updating your profile
                description = 'You have updated your privacy settings'
                user_profile_update = UserActivity.objects.create(
                    user = currentUser,
                    description = description,
                    status = 1
                )

                return redirect('home_page')
    AccountUpdate = AccountUpdateForm(instance=currentUser)
    UserUpdate = UserUpdateForm(instance=currentProfile)
    PasswordUpdate = PasswordUpdateForm()
    InfoUpdate = InfoUpdateForm(instance=currentProfile)
    PrivacyUpdate = PrivacyUpdateForm()

    parameters = {
        'currentUser':currentUser,
        'currentProfile':currentProfile,
        'currentPrivacy':currentPrivacy,
        'AccountUpdate':AccountUpdate,
        'UserUpdate':UserUpdate,
        'PasswordUpdate':PasswordUpdate,
        'InfoUpdate':InfoUpdate,
        'PrivacyUpdate':PrivacyUpdate,
        'passwordMessage':passwordMessage,
    }
    return render(request, 'content/user_settings.html', parameters)

def logoutPage(request):
    # the following 3 lines will check to see if there is a username in the session
    # which means that there is someone logged in and it will give them access to
    # opentab.
    if 'username' not in request.session:
        return redirect('login')
    else:
        # the following will dump the stored username in the session and redirect
        # to the login page.
        username = request.session['username']
        request.session.pop('username')
        return redirect('login')

#----------- FRIENDING SYSTEM -------------------------------------------

# send a friend request
def sendRequest(request, requested):
    # grab the user that is logged in
    currentUser = loggedInUser(request)
    # the following will grab the user object with the username that was submitted
    requestedUser = User.objects.get(username = requested)
    # the following created a new record in the request table within the database.
    if requestedUser:
        new_request = Request.objects.create(
            user = currentUser,
            requested = requestedUser,
        )
        # create an activity to notify receiver of friend request
        description = currentUser.username + ' has send you a friend request'
        request_activity = UserActivity.objects.create(
            user = requestedUser,
            description = description,
            status = 1,
        )
    return redirect('home_page')

# The following method will process the acceptaance of a friend request.
def acceptRequest(request, accepted):
    currentUser = loggedInUser(request)
    acceptedUser = User.objects.get(username = accepted)
    # a new record will be added to the Friend table in teh database that will
    # be later used as a way to display all of a users friends.
    new_friend = Friend.objects.create(
        user = currentUser,
        friend = acceptedUser,
        category = 1
    )
    # creates two user activities that notify requester and accepter that they are now friends
    accepted_description = 'You and ' + acceptedUser.username + ' are now friends'
    friend_description = 'You and ' + currentUser.username + ' are now friends'
    accepted_activity = UserActivity.objects.create(
        user = currentUser,
        description = accepted_description,
        status = 1
    )
    friend_activity = UserActivity.objects.create(
        user = acceptedUser,
        description = friend_description,
        status = 1
    )
    # after the new friend record is created, the original friend request is deleted
    requests = Request.objects.filter(requested = currentUser).all()
    for request in requests:
        if request.user == acceptedUser.username:
            request.delete()
    return redirect('home_page')

#-------------- USER ACCOUNTS LINKED -----------------------------------
def userAccounts(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    listedAccounts = SynapseAccounts.objects.filter(user = currentUser).all()

    parameters = {
        'currentUser':currentUser,
        'listedAccounts':listedAccounts,
    }

    return render(request, 'content/user_accounts.html', parameters)


#-------------- SINGLE EXPENSES ----------------------------------------

# shows all of the users single transactions
def userExpenses(request):
    # grabs the logged in users profile and account
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # grabs all of the activities related to expenses for the user
    activities = UserActivity.objects.filter(user = currentUser).all()
    # passes all of the parameters to the html template
    parameters = {
        'currentUser':currentUser,
        'activities':activities,
    }
    return render(request, 'content/user_expenses.html', parameters)

def addExpenseSingle(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    friender = Friend.objects.filter(user = currentUser.username).all()
    friended = Friend.objects.filter(friend = currentUser).all()

    friends = friender | friended

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd['name']
            location = cd['location']
            split = cd['split']
            reference = generateReferenceNumber()
            new_expense = Expense.objects.create(
                user = currentUser,
                name = name,
                location = location,
                split = split,
                reference = reference,
                created_by = currentUser.username,
            )
            description = 'You created a new expense: ' + new_expense.name + ' - ' + new_expense.location
            expense_activity = UserActivity.objects.create(
                user = currentUser,
                expense = new_expense,
                description = description,
                reference = reference,
                validation = 1,
            )
            for friend in friends:
                if friend.user == currentUser.username:
                    if friend.friend.username in request.POST:
                        new_expense = Expense.objects.create(
                             user = friend.friend,
                             name = name,
                             location = location,
                             split = split,
                             reference = reference,
                             created_by = currentUser.username,
                        )
                if friend.friend == currentUser:
                    if friend.user in request.POST:
                        friend = User.objects.get(username = friend.user)
                        new_expense = Expense.objects.create(
                             user = friend,
                             name = name,
                             location = location,
                             split = split,
                             reference = reference,
                             created_by = currentUser.username,
                        )
                description = currentUser.username + ' created a new expense: ' + new_expense.name + ' - ' + new_expense.location
                expense_activity = UserActivity.objects.create(
                    user = new_expense.user,
                    expense = new_expense,
                    description = description,
                    accepted = 1,
                    reference = reference,
                    validation = 1
                )
        if split == 1:
            return redirect('update_expense_even_single', reference = reference)
        if split == 2:
            return redirect('update_expense_individual_single', reference = reference)

    else:
        form = ExpenseForm()
        message = 'Please fill out the form'
        parameters = {
            'form':form,
            'message':message,
            'friends':friends,
            'currentUser':currentUser,
        }
        return render(request, 'content/single_expense.html', parameters)

def updateExpenseEvenSingle(request, reference):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    expenses = Expense.objects.filter(reference = reference).all()
    expenses_count = Expense.objects.filter(reference = reference).count()
    host = currentUser
    if request.method == 'POST':
        form = UpdateExpenseEvenForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            amount = cd['amount']
            userAmount = SplitEven(expenses_count, amount)
            for expense in expenses:
                amount = expense.amount
                update_expense = expense
                update_expense.amount = userAmount
                update_expense.save()
                if expense.user != currentUser:
                    user_decription = 'You owe ' + host.username + ' $' + str(userAmount) + ' for ' + expense.name
                    user_activity = UserActivity.objects.create(
                        user = expense.user,
                        expense = expense,
                        description = user_decription,
                        accepted = 1,
                        status = 1,
                        reference = reference,
                        validation = 2,
                    )
                    host_description = expense.user.username + ' owes you $' + str(userAmount) + ' for ' + expense.name
                    host_activity = UserActivity.objects.create(
                        user = host,
                        expense = expense,
                        description = host_description,
                        accepted = 1,
                        status = 1,
                        reference = reference,
                        validation = 1,
                    )
            return redirect('user_expenses')
    else:
        message = 'Please complete the form '
        form = UpdateExpenseEvenForm()
        parameters = {
            'message':message,
            'form':form,
            'expenses':expenses,
        }
        return render(request, 'content/update_expense_even.html', parameters)

def updateExpenseIndividualSingle(request, reference):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    expenses = Expense.objects.filter(reference = reference)
    expenses_count = Expense.objects.filter(reference = reference).count()
    host = currentUser
    SplitFormSet = formset_factory(UpdateExpenseIndividualForm, extra=expenses_count)
    if request.method == 'POST':
        formSet = SplitFormSet(request.POST)
        if 'tax' in request.POST:
            tax = request.POST['tax']
            amount = Decimal(tax)
            individual_tax = SplitEven(expenses_count, amount)
        if 'tip' in request.POST:
            tip = request.POST['tip']
            amount = Decimal(tip)
            individual_tip = SplitEven(expenses_count, amount)
        if formSet.is_valid():
            count = 0
            for form in formSet:
                if form.is_valid:
                    cd = form.cleaned_data
                    amount = cd['amount']
                    description = cd['description']
                    total_amount = amount + individual_tip + individual_tax
                    expense = expenses[count]
                    if expense.user != currentUser:
                        update_expense = expense
                        update_expense.amount = total_amount
                        update_expense.description = description
                        update_expense.save()
                        user_description = 'You owe ' + host.username + ' $' + str(total_amount) + ' for ' + expense.name + ' - ' + description
                        user_activity = UserActivity.objects.create(
                            user = expense.user,
                            expense = expense,
                            description = user_description,
                            accepted = 1,
                            status = 1,
                            reference = reference,
                            validation = 2,
                        )
                        host_description = expense.user.username + ' owes you $' + str(userAmount) + ' for ' + expense.name + ' - ' + description
                        host_activity = UserActivity.objects.create(
                            user = currentUser,
                            expense = expense,
                            description = host_decription,
                            accepted = 1,
                            status = 1,
                            reference = reference,
                            validation = 1,
                        )
                count = count + 1
            return redirect('user_expenses')
    else:
        form = SplitFormSet()
        message = 'Please complete the form below'
        parameters = {
            'message':message,
            'form':form,
            'expenses':expenses,
            # 'form_user':form_user,
        }
        return render(request, 'content/update_expense_individual.html', parameters)

def verifyExpenseSingle(request, activityId):
    currentUser = loggedInUser(request)

    currentActivity = UserActivity.objects.get(id = activityId)

    currentExpense = currentActivity.expense
    host = currentActivity.expense.created_by

    update_expense = currentExpense
    update_expense.status = 2
    update_expense.save()

    description = 'You have transfered ' + str(currentExpense.amount) + ' to ' + host + ' for ' + currentExpense.name
    new_activity = UserActivity.objects.create(
        user = currentUser,
        expense = currentExpense,
        description = description,
        status = 2,
        accepted = 2,
        validation = 3,
        reference = currentActivity.reference,
    )

    currentActivity.delete()

    return redirect('user_expenses')

#------------ GROUPS --------------------------------------------
def userGroups(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    members = Member.objects.filter(user = currentUser).all()
    if request.method == "POST":
        cheese = 'hello'
    else:
        parameters = {
            'currentUser':currentUser,
            'members':members,
        }
        return render(request, 'content/user_groups.html', parameters)

def createGroup(request):
    currentUser = loggedInUser(request)
    # following is all of th actions that are taken after the form is submitted
    if request.method == 'POST':
        # the following few lines will get the submitted form and create a reference
        # code that is going to be used later.
        # it will also assign the user that created the group
        form = CreateGroupForm(request.POST)
        referenceCode = generateReferenceNumber()
        # the following validated the actual form to ensure that it was filled out
        # with the correct inforamtion
        if form.is_valid():
            cd = form.cleaned_data
            name = cd['name']
            description = cd['description']
            # the new_group creates an isntance of the new group and saved it into
            # the database once it is created.
            new_group = Group.objects.create(
                name = name,
                description = description,
                reference_code = referenceCode,
                created_by = currentUser,
            )

            user_description = 'You created a new group - ' + name

            user_activity = UserActivity.objects.create(
                user = currentUser,
                description = user_description,
                status = 1,
            )


            # return redirect('home_page')
            return redirect('add_members', groupId=new_group.id)
            #return redirect('accounts')
            #return redirect(reverse('add_members', args=[new_group.id]))
    else:
        # the following is the storing of the forms
        form = CreateGroupForm()
        message = 'enter group info below'
    # the following are all the objects that are going to be passed to the
    # rendering remplate
        parameters = {
            'form':form,
            'message':message,
        }
    return render(request, 'content/create_group.html', parameters)

def addMembers(request, groupId):
    currentUser = loggedInUser(request)
    # the following line will grab the group object that members will be added ot and
    # stored in a variable that will be referenced later.
    groups = Group.objects.filter(id = groupId).all()
    # the following will grab all of the member objects that are related to the logged
    # in user.
    group = Group.objects.get(id = groupId)
    users = User.objects.all()
    friends = Friend.objects.all()
    # the form is similar to the form submition above for reference
    if request.method == "POST":
        # the following sets the current user as a member of the group once the
        # group is created as a default
        new_default_member = Member.objects.create(
            user = currentUser,
            group = group,
            status = 2,
        )

        default_description = currentUser.username + ' created ' + group.name
        default_activity = GroupActivity.objects.create(
            group = group,
            description = default_description,
        )
        # the following will scroll through every user in the users table
        for friend in friends:
            # it will then check to see if the usersname was returned in the request.
            # if the username was checked, it will be returned, otherwise it will not
            # be passed.
            if friend.user == currentUser.username:
                selected_user = User.objects.get(username = friend.friend.username)
                if selected_user.username in request.POST:
                    new_member = Member.objects.create(
                        user = selected_user,
                        group = group,
                        status = 1,
                    )

                    friend_description = currentUser.username + ' added you to ' + group.name
                    group_description = currentUser.username + ' added ' + selected_user.username + ' to ' + group.name

                    group_member_activity = GroupActivity.objects.create(
                        user = selected_user,
                        group = group,
                        description = group_description,
                        general = 1
                    )

                    friend_member_activity = GroupActivity.objects.create(
                        user = selected_user,
                        group = group,
                        description = friend_description,
                        general = 2,
                    )

            if friend.friend.username == currentUser.username:
                selected_user = User.objects.get(username = friend.user)
                print(selected_user)
                if selected_user.username in request.POST:
                    new_member = Member.objects.create(
                        user = selected_user,
                        group = group,
                        status = 1,
                    )

                    friend_description = currentUser.username + ' added you to ' + group.name
                    group_description = currentUser.username + ' added ' + selected_user.username + ' to ' + group.name

                    group_member_activity = GroupActivity.objects.create(
                        user = selected_user,
                        group = group,
                        description = group_description,
                        general = 1
                    )

                    friend_member_activity = GroupActivity.objects.create(
                        user = selected_user,
                        group = group,
                        description = friend_description,
                        general = 2
                    )

                # next three lines will keep track and updated the group count every time that
                # a new user is added to the specific group that is selected.
                updated_group = group
                updated_group.count = updated_group.count + 1
                updated_group.save()
        return redirect('group_home', groupId=group.id)
    else:
        # the form that the user fills out will display all of the members of the
        # app and the current user will select the checkbox next to the name
        # of the user that he wants to add to the group. THIS WILL CHANGE TO DISPLAY
        # FRIENDS AFTER THE FRIENDS MODEL AND FUNCTION ARE CREATED
        message = 'add members below'
        params = {
            'message':message,
            'group':group,
            'users':users,
            'friends':friends,
            'currentUser':currentUser,
        }
    return render(request, 'content/add_members.html', params)

def groupHome(request, groupId):
    currentUser = loggedInUser(request)
    group = Member.objects.filter(user = currentUser).filter(group = groupId).first()
    # the following is going to be the currentGroup by groupId
    currentGroup = Group.objects.get(id = groupId)
    # the following is the group object with the id that is passed in the url
    # group = Group.objects.get(name = groupName)
    members = Member.objects.filter(group = group.group).all()
    for member in members:
        if member.status == 2:
            host = member

    activities = GroupActivity.objects.filter(group = currentGroup).all()

    expenses = Expense.objects.filter(group = group.group).all()

    parameters = {
        'members':members,
        'group':group,
        'currentGroup':currentGroup,
        'currentUser':currentUser,
        'expenses':expenses,
        'host':host,
        'activities':activities,
    }
    return render(request, 'content/group_home.html', parameters)

def groupInformation(request, groupId):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    currentGroup = Group.objects.get(id = groupId)

    host = None

    members = Member.objects.filter(group = currentGroup).all()
    for member in members:
        if member.status == 2:
            host = member

    parameters = {
        'currentUser':currentUser,
        'currentGroup':currentGroup,
        'members':members,
        'host':host
    }

    return render(request, 'content/group_info.html', parameters)

def selectHostMember(request, groupId, memberName):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    currentGroup = Group.objects.get(id = groupId)
    members = Member.objects.filter(group = currentGroup)
    for member in members:
        if member.status == 2:
            host = member
            print(host.user.username)
        if member.user.username == memberName:
            selectedMember = member
            print(selectedMember.user.username)

    old_host = host
    old_host.status = 1
    old_host.save()

    new_host = selectedMember
    new_host.status = 2
    new_host.save()

    group_description = selectedMember.user.username + ' is the new group host'
    group_activity = GroupActivity.objects.create(
        group = currentGroup,
        description = group_description,
    )

    return redirect('group_home', groupId = currentGroup.id)

def createChecklist(request, groupId):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    currentGroup = Group.objects.get(id = groupId)
    members = Member.objects.filter(group = currentGroup)
    for member in members:
        if member.status == 2:
            host = member.user

    if request.method == 'POST':
        form = CreateChecklistForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd['name']
            amount1 = cd['amount1']
            item1 = cd['item1']
            reference = generateReferenceNumber()
            count = 0
            for member in members:
                if member.user.username in request.POST:
                    new_item = Checklist.objects.create(
                        user = member.user,
                        group = currentGroup,
                        total = amount1,
                        name = item1,
                        reference = reference,
                        created_by = host
                    )
                    print(new_item)
                count = count + 1
            return redirect('group_home', currentGroup.id)
    else:
        form = CreateChecklistForm()
        parameters = {
            'form':form,
            'members':members,
            'group':currentGroup,
        }
        return render(request, 'content/create_checklist.html', parameters)

def addExpense(request, groupId):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    currentGroup = Group.objects.get(id = groupId)
    members = Member.objects.filter(group = currentGroup).all()

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd['name']
            location = cd['location']
            split = cd['split']
            for member in members:
                if member.user.username in request.POST:
                    new_expense = Expense.objects.create(
                        user = member.user,
                        group = currentGroup,
                        name = name,
                        location = location,
                        split = split,
                    )
            description = 'New expense: ' + new_expense.name + ' - ' + new_expense.location
            expense_activity = GroupActivity.objects.create(
                group = currentGroup,
                expense = new_expense,
                description = description
            )

        if split == 1:
            return redirect('update_expense_even', groupId = currentGroup.id, groupName = name)
        if split == 2:
            return redirect('update_expense_individual', groupId = currentGroup.id, groupName = name)
    else:
        form = ExpenseForm()
        message = 'Please fill out the form'
        parameters = {
            'form':form,
            'message':message,
            'members':members,
            'currentGroup':currentGroup,
        }
        return render(request, 'content/add_expense.html', parameters)

def updateExpenseEven(request, groupId, groupName):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    currentGroup = Group.objects.get(id = groupId)
    host = Member.objects.filter(group = groupId).filter(status = 2).first()
    expenses = Expense.objects.filter(group = currentGroup).filter(name = groupName).all()
    expenses_count = Expense.objects.filter(group = currentGroup).filter(name = groupName).count()
    if request.method == "POST":
        form = UpdateExpenseEvenForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            amount = cd['amount']
            userAmount = SplitEven(expenses_count, amount)
            # the followig is going to update the expenses that were created with the
            # split amounts and description for the expense
            for expense in expenses:
                amount = expense.amount
                update_expense = expense
                update_expense.amount = userAmount
                update_expense.save()

                if expense.user != currentUser:

                    user_description = 'You owe ' + host.user.username + ' $' + str(userAmount) + ' for ' + expense.name
                    user_activity = GroupActivity.objects.create(
                        user = expense.user,
                        group = currentGroup,
                        expense = expense,
                        description = user_description,
                        general = 2,
                        validation = 2,
                        host = currentUser.username,
                    )


                    group_description = expense.user.username + ' owes ' + host.user.username + ' $' + str(userAmount) + ' for ' + expense.name
                    group_activity = GroupActivity.objects.create(
                        user = expense.user,
                        group = currentGroup,
                        expense = expense,
                        description = group_description,
                        general = 1,
                        validation = 2,
                        host = currentUser.username
                    )
                # if expense.user != host.user:
            return redirect('group_home', groupId = currentGroup.id)
    else:
        message = 'Please complete form below'
        form = UpdateExpenseEvenForm()
        parameters = {
            'message':message,
            'form':form,
            'currentGroup':currentGroup,
            'expenses':expenses,
        }
        return render(request, 'content/update_expense_even.html', parameters)

def updateExpenseIndividual(request, groupId, groupName):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    currentGroup = Group.objects.get(id = groupId)
    host = Member.objects.filter(group = groupId).filter(status = 2).first()
    expenses = Expense.objects.filter(group = currentGroup).filter(name = groupName).all()
    expenses_count = Expense.objects.filter(group = currentGroup).filter(name = groupName).count()
    SplitFormSet = formset_factory(UpdateExpenseIndividualForm, extra=expenses_count)
    # form_user = zip(expenses, SplitFormSet)
    if request.method == 'POST':
        formSet = SplitFormSet(request.POST)
        if 'tax' in request.POST:
            tax = request.POST['tax']
            amount = Decimal(tax)
            individual_tax = SplitEven(expenses_count, amount)
        if 'tip' in request.POST:
            tip = request.POST['tip']
            amount = Decimal(tip)
            individual_tip = SplitEven(expenses_count, amount)
        if formSet.is_valid():
            count = 0
            for form in formSet:
                cd = form.cleaned_data
                amount = cd['amount']
                description = cd['description']
                total_amount = amount + individual_tip + individual_tax
                expense = expenses[count]
                update_expense = expense
                update_expense.amount = total_amount
                update_expense.description = description
                update_expense.save()
                # if expense.user != host.user:

                user_description = 'You owe ' + host.user.username + ' $' + str(total_amount) + ' for ' + description
                group_description = expense.user.username + ' owe ' + host.user.username + ' $' + str(total_amount) + ' for ' + description

                user_activity = GroupActivity.objects.create(
                    user = expense.user,
                    group = currentGroup,
                    expense = expense,
                    description = user_description,
                    general = 2,
                    validation = 2,
                )

                group_activity = GroupActivity.objects.create(
                    user = expense.user,
                    group = currentGroup,
                    expense = expense,
                    description = group_description,
                    general = 1,
                    validation = 2,
                )

                count = count + 1
        return redirect('group_home', groupId = currentGroup.id)
    else:
        form = SplitFormSet()
        message = 'Please complete the form below'
        parameters = {
            'message':message,
            'form':form,
            'currentGroup':currentGroup,
            'expenses':expenses,
            # 'form_user':form_user,
        }
        return render(request, 'content/update_expense_individual.html', parameters)

def verifyExpense(request, expenseId, activityId):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    currentExpense = Expense.objects.get(id = expenseId)
    currentExpense.status = 2
    currentExpense.save()

    currentActivity = GroupActivity.objects.get(id = activityId)
    activity_number = currentActivity.id + 1
    secondActivity = GroupActivity.objects.get(id = activity_number)

    host = currentActivity.host

    user_description = 'You transfered $' + str(currentExpense.amount) + ' to ' + host + ' for ' + currentExpense.description
    group_description = currentUser.username + ' transfered $' + str(currentExpense.amount) + ' to ' + host + ' for ' + currentExpense.description

    user_activity = GroupActivity.objects.create(
        user = currentUser,
        group = currentExpense.group,
        expense = currentExpense,
        description = user_description,
        general = 2
    )

    group_description = GroupActivity.objects.create(
        user = currentUser,
        group = currentExpense.group,
        expense = currentExpense,
        description = group_description,
        general = 1
    )

    currentActivity.delete()
    secondActivity.delete()

    group_id = currentExpense.group.id
    return redirect('group_home', group_id)

def leaveGroup(request, groupId):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    currentGroup = Group.objects.get(id = groupId)
    currentMember = Member.objects.filter(user = currentUser).filter(group = currentGroup).first()
    groupActivity = GroupActivity.objects.filter(user = currentUser).filter(group = currentGroup).all()

    members = Member.objects.filter(group = currentGroup).all()
    for member in members:
        if member.status == 2:
            host = member

    if host.user == currentUser:
        print(' you are the host ')
        return redirect('group_home', groupId)

    for activity in groupActivity:
        if activity.validation == 2:
            print(' you have expenses that need validation ')
            return redirect('group_home', groupId)

    delete_member = currentMember
    delete_member.delete()

    description = currentUser.username + ' has left the group'
    new_activity = GroupActivity.objects.create(
        user = host.user,
        group = currentGroup,
        description = description,
        general = 2,
    )
    print(' you have left the group ')

    return redirect('user_groups')

#------------- GENERAL METHODS AND FUNCTIONS -------------------------------
def clearAllActivities(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    activities = UserActivity.objects.filter(user = currentUser).all()

    for activity in activities:
        update_activity = activity
        update_activity.status = 2
        update_activity.save()
    return redirect('user_home')

# the following is in charge of spliting an amount by number of people.
def SplitEven(count, amount):
    # the following will divide the amount passed though by the number of members
    # that was stored above.
    split_amount = amount/count
    # the following ensure that the result of the divide is rounded to 2 decimal
    # space.
    rounded_amount = round(split_amount, 2)
    return rounded_amount

def loggedInUser(request):
    if 'username' not in request.session:
        return redirect('login')
    else:
        username = request.session['username']
        currentUser = User.objects.get(username = username)
        return currentUser

def updateSessionUsername(request, new_username):
    if 'username' in request.session:
        request.session.pop('username')
        request.session['username'] = new_username
        return redirect('home_page')

# the view / method is called to generate a random number that is stored as the
# groups reference number for later use within the aaplication.
def generateReferenceNumber():
    reference = randint(1, 2147483646)
    return(reference)

def numberify(request, number):
    phone = '-'.join([number[:3], number[3:6], number[6:]])
    return phone

def setPrivacy(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    if currentProfile.privacy == 1:
        new_privacy = Privacy.objects.create(
            user = currentUser,
            groups = 1,
            friends = 1,
            expenses = 1,
            searchable = 1,
        )

    return new_privacy

def templateTesting(request):
    cheese = 'cheese'
    parameters = {
        'cheese':cheese,
    }
    return render(reqest, 'content/template_testing.html', parameters)

#------------- SYNAPSE INTEGRATION -----------------------------------
def createUserSynapse(request):
    # the following grabs the current suer and profile for the current user which
    # will be used to retrieve and update informaiton pretaining to the new user
    currentUser = loggedInUser(request)
    profile= Profile.objects.get(user = currentUser)

    # the following saves a reference to the current profile
    currentProfile = profile
    # the following lines will store inforaiton that is sent with the new user
    # request rather than enter it directly to the arguments
    legal_name = currentProfile.first_name + " " + currentProfile.last_name
    note = legal_name + " has just created his synapse profile "
    supp_id = generateReferenceNumber()
    cip_tag = currentUser.id
    # the following is all of the information that is required in order to make a
    # new user within the Synapse application
    args = {
        'email':str(currentUser.email),
        'phone_number':str(currentProfile.phone),
        'legal_name':str(legal_name),
        'note': str(note),
        'supp_id':str(supp_id),
        'is_business':False,
        'cip_tag':cip_tag,
    }
    # the following is the request to the synapse api as well as the returned
    # json that contains information that needs to ba saved in local database
    create_user = SynapseUser.create(client, **args)
    response = create_user.json
    # the following updates the current profile to add the users synapse id within
    # the local database.
    if response:
        synapse_id = response['_id']
        updateProfile = currentProfile
        updateProfile.synapse_id = synapse_id
        updateProfile.save()

# the following method is where the current user will go to retreive their synapse
# account informaiton in order to make other synapse requests.
def retreiveUserSynapse(request):
    # the following is going to be where the record for the logged in user is grabed
    # as well as the profile.
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # the following is the current users Synapse Id required for calling the API
    user_id = currentProfile.synapse_id
    # the following will make a synapse request which will return the users
    # account informaiton in a json format
    searchedUser = SynapseUser.by_id(client, str(user_id))
    # the folloiwng will check to make sure there is object returned before returning
    # it to the method call.
    if searchedUser:
        print(searcheduser)
        return searchedUser

# The following is the first part of the linking your bank account through login
# to your bank account. This will grab the form and pass it in order to complete
# the linking bank accounts processing.
def synapseLogin(request):
    # the following willl check and make sure that there is a user that is logged in
    # and grab their profile.
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # the following is going to grab the form that is submitted and process the form
    if request.method == 'POST':
        # the followig will grab the form from the POST
        form = synapseLoginFOrm(request.POST)
        # this will make sure that the form values are valid. If they are valid,
        # the form will be sent to a processing method that will complete the
        # processing
        if form.is_valid():
            authorizeLogin(request, form)
            saveLogin(request)
            return redirect('user_accounts')
    # if there was no form submitted, the following is where the form will be
    # rendered with other additional information that is needed.
    else:
        form = synapseLoginForm()
        message = "Enter you bank login credentials"
        parameters = {
            'form':form,
        }
        return render(request, 'content/synapse_login.html', parameters)

def synapseAccount(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    if request.method == 'POST':
        form = synapseAccountForm(request.POST)
        if form.is_valid():
            authorizeAccount(request, form)
            saveLogin(request)
            return redirect('user_accounts')
    else:
        form = synapseAccountForm()
        parameters = {
            'form':form,
        }
        return render(request, 'content/synapse_account.html', parameters)

# the followig method is going to do the full processing of the linkig bank account
# form and complete the request action.
def authorizeLogin(request, form):
    # this will grab the currently logged in user and the users profile for later
    # reference
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # the following grabs the logged in users synapse id from his profile.
    user_id = currentProfile.synapse_id
    # the following will send a request to get the users synapse profile from the
    # api and later user that response object.
    synapseUser = SynapseUser.by_id(client, str(user_id))
    print(synapseUser)
    # the following section is going to be the informaiton passed from the form that
    # was submitted, commented out for testing
    # cd = form.cleaned_data
    # bank_code = cd['bank_code']
    # bank_id = cd['bank_id']
    # bank_pw = cd['bank_password']
    # the following are just testing values in sandbox to make sure the processing
    # works and is able to send the request and receive the response to process
    bank_id = 'synapse_good'
    bank_pw = 'test1234'
    bank_code = 'fake'
    print(bank_code)
    print(bank_id)
    print(bank_pw)
    # the following is the object that is going to be passed with the response
    args = {
        'bank_name':bank_code,
        'username':bank_id,
        'password':bank_pw,
    }
    print(args)
    # the followig is the actual request that will process the request and return
    # a response that will then be verified
    ach_us = AchUsNode.create_via_bank_login(synapseUser, **args)
    # the following will check to see if mfa verification is needed for the specified
    # bank
    verification = ach_us.mfa_verified
    print(verification)
    # If the mfa verification is needed, the following will simply verify the account
    # and make the account verified.
    if verification == False:
        ach_us.mfa_message
        nodes = ach_us.answer_mfa('test_answer')
        ach_us.mfa_verified
    print(ach_us)

def authorizeAccount(request, form):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    user_id = currentProfile.synapse_id

    synapseUser = SynapseUser.by_id(client, str(user_id))

    required = {
        'nickname': 'Fake Account',
        'account_number': '1232225674134',
        'routing_number': '051000017',
        'account_type': 'PERSONAL',
        'account_class': 'CHECKING'
    }
    print(required)

    account = AchUsNode.create(synapseUser, **required)
    print(account)

def saveLogin(request):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)
    # the following will grab the users synapse id from the users local profile.
    user_id = currentProfile.synapse_id
    # the following will grab the entire synapse profile by sending an api request
    # with the users synapse profile.
    synapseUser = SynapseUser.by_id(client, str(user_id))
    # the following are options for how to display and structure the response for
    # all of the different nodes linked to the users account
    options = {
        'page':1,
        'per_page':20,
        'type': 'ACH-US',
    }
    # the following is the request and response with all of the users linked nodes
    # ready to be processed and storage of certain information.
    nodes = Node.all(synapseUser, **options)

    for node in nodes:
        print(node)
        node_json = node.json
        node_id = node_json['_id']
        node_name = node_json['info']['nickname']
        node_class = node_json['info']['class']
        node_bank_name = node_json['info']['bank_name']
        node_balance = node_json['info']['balance']['amount']
        node_currency = node_json['info']['balance']['currency']
        account = SynapseAccounts.objects.filter(user = currentUser).filter(account_id = node_id).first()
        if account == None:
            new_accout = SynapseAccounts.objects.create(
                user = currentUser,
                name = node_name,
                account_id = node_id,
                account_class = node_class,
                bank_name = node_bank_name,
                balance = node_balance,
                main = 1
            )
        if account:
            if account.balance != node_balance:
                update_account = account
                update_account.balance = node_balance
                update_account.save()

    return redirect('user_accounts')

def defaultLinkedAccount(request, accountId):
    currentUser = loggedInUser(request)
    currentProfile = Profile.objects.get(user = currentUser)

    accounts = SynapseAccounts.objects.filter(user = currentUser).all()
    for account in accounts:
        if account.main == 2:
            if account.id != accountId:
                update_account = account
                update_account.main = 1
                update_account.save()

    currentAccount = SynapseAccounts.objects.get(id = accountId)

    update_account = currentAccount
    update_account.main = 2
    update_account.save()

    return redirect('user_accounts')
