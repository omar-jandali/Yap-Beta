from django.conf.urls import url
from . import views

# the following are all the urls that are needed
urlpatterns = [
    url(r'^test$', views.Test, name='test'),
    url(r'^$', views.userGroups, name='home_page'),
    url(r'^login$', views.loginPage, name='login'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^setup_profile/$', views.profileSetup, name='profile_setup'),
    url(r'^settings/$', views.userSettings, name='user_settings'),
    url(r'^profile/$', views.userHome, name='user_home'),
    url(r'^searched/$', views.searchedUser, name='user_search'),
    url(r'^groups/$', views.userGroups, name='user_groups'),
    url(r'^accounts/$', views.userAccounts, name='user_accounts'),
    url(r'^expenses/$', views.userExpenses, name='user_expenses'),
    url(r'^createGroup/$', views.createGroup, name='create_group'),
    url(r'^single_expense/$', views.addExpenseSingle, name='single_expense'),
    url(r'^save_login/$', views.saveLogin, name='save_login'),
    url(r'^clear_all_activities/$', views.clearAllActivities, name='clear_all_activities'),
    url(r'^logout$', views.logoutPage, name='logout'),
    # the following is used for requests
    url(r'^(?P<requested>[\w+]+)/sendRequest/$', views.sendRequest, name="send_request"),
    url(r'^(?P<accepted>[\w+]+)/acceptRequest/$', views.acceptRequest, name="accept_request"),
    # the following two are for synapse
    url(r'^synapse_login/$', views.synapseLogin, name='synapse_login'),
    url(r'^synapse_account/$', views.synapseAccount, name='synapse_account'),
    url(r'^(?P<accountId>[\w+]+)/setDefaultAccount/$', views.defaultLinkedAccount,
        name="set_default_account"),
    url(r'^(?P<userName>[\w+]+)/$', views.userProfile, name='user_profile'),
    # groups
    url(r'^createGroup/$', views.createGroup, name='create_group'),
    url(r'^(?P<groupId>[0-9]+)/add_members/$', views.addMembers, name='add_members'),
    url(r'^(?P<groupId>[0-9]+)/group$', views.groupHome, name='group_home'),
    url(r'^(?P<groupId>[0-9]+)/group_info/$', views.groupInformation, name='group_info'),
    url(r'^(?P<groupId>[0-9]+)/add_expense/$', views.addExpense, name="add_expense"),
    url(r'^(?P<groupId>[0-9]+)/create_checklist/$', views.createChecklist, name='create_checklist'),
    url(r'^(?P<groupId>[0-9]+)/(?P<groupName>[\w+]+)/update_expense_even/$',
        views.updateExpenseEven, name="update_expense_even"),
    url(r'^(?P<groupId>[0-9]+)/(?P<groupName>[\w+]+)/update_expense_individual/$',
        views.updateExpenseIndividual, name="update_expense_individual"),
    url(r'^(?P<groupId>[0-9]+)/(?P<memberName>[\w+]+)/select_host_member/$', views.selectHostMember,
        name='select_host_member'),
    url(r'^(?P<groupId>[0-9]+)/leave_group/$', views.leaveGroup, name="leave_group"),
    # single expenses
    url(r'^(?P<reference>[0-9]+)/update_expense_even_single/$',
        views.updateExpenseEvenSingle, name="update_expense_even_single"),
    url(r'^(?P<reference>[0-9]+)/update_expense_individual_single/$',
        views.updateExpenseIndividualSingle, name="update_expense_individual_single"),
    url(r'^(?P<expenseId>[0-9]+)/(?P<activityId>[0-9]+)/verify_expense/$', views.verifyExpense, name='verify_expense'),
    url(r'^(?P<activityId>[0-9]+)/verify_expense/$', views.verifyExpenseSingle, name='verify_expense_single'),
]
