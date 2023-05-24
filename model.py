'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import sqlite3

import view
import random
from sql import SQLDatabase
from time import sleep

# Initialise our views, all arguments are defaults for the template
page_view = view.View()

#-----------------------------------------------------------------------------
# Profile
#-----------------------------------------------------------------------------

def profile():
    '''
        profile
        Returns the view for user profile
    '''
    return page_view("profile")

def get_params_admin_page(users_connection):
    user_ids = users_connection.get_all_user_id()
    usernames = users_connection.get_all_username()
    user_admins = users_connection.get_all_user_admins()

    ls = []; i = 0
    while i < len(usernames):
        ls.append(user_ids[i][0])
        ls.append(usernames[i][0])
        ls.append(user_admins[i][0])
        i+=1

    return ls

def admin_page():
    users_connection = SQLDatabase("Users.db")
    ls = get_params_admin_page(users_connection)
    return page_view("admin-page", ls_param=ls)

def admin_page_add_user(username, password):
    users_connection = SQLDatabase("Users.db")
    users_connection.add_user(username, password, password)

    ls = get_params_admin_page(users_connection)
    return page_view("admin-page", ls_param=ls)

def delete_user(id):
    users_connection = SQLDatabase("Users.db")
    users_connection.delete_user(id)

    ls = get_params_admin_page(users_connection)
    return page_view("admin-page", ls_param=ls)

def give_user_admin_rights(id):
    users_connection = SQLDatabase("Users.db")
    users_connection.give_user_admin_rights(id);

    ls = get_params_admin_page(users_connection)
    return page_view("admin-page", ls_param=ls)

def create_account_form():
    '''
        create_account_form
        Returns the view for the create_account_form
    '''


    return page_view("create_account")

def create_account(username, password, passwordcheck):
    '''
        create_account
        Creates new User and stores in database
        :: username      :: The username
        :: password      :: The password
        :: passwordcheck :: The password entered again
        Returns either a view for account successfully created, or a view for account username taken
    '''

    users_connection = SQLDatabase("Users.db")
    result = users_connection.add_user(username, password, passwordcheck)
    if result == "added":
        return page_view("valid-create", name=username)
    else:
        return page_view("invalid", reason=result)
    
def change_account_key(username, public_key):
    users_connection = SQLDatabase("Users.db")
    users_connection.update_key(username, public_key)
    return page_view("valid-key")

def get_dh_key(username, message, sender):
    users_connection = SQLDatabase("Users.db")
    exists = users_connection.username_exists(username)
    if exists:
        p_key = users_connection.get_key(username)
        return page_view("valid-dh", p=p_key,name=username, m=message,s=sender)
    else:
        return page_view("invalid-dh")
    
def send_message(receiver_name, message, sender, ivr):
    users_connection = SQLDatabase("Users.db")
    exists = users_connection.username_exists(receiver_name)
    users_connection.update_message(receiver_name, message, sender, ivr)
    
    if exists:
        return page_view("valid-send")
    else:
        return page_view("invalid")

def discussion():
    posts_connection = SQLDatabase("Posts.db")
    #post_ids = posts_connection.get_all_post_Id()
    post_usernames = posts_connection.get_all_post_name()
    post_contents = posts_connection.get_all_post_content()

    ls = []; i = 0
    while i < len(post_usernames):
        #ls.append(post_ids[i][0])
        ls.append(post_usernames[i][0])
        ls.append(post_contents[i][0])
        i+=1

    #discussion no longer needs all the other args, ls_param contains everything
    return page_view("discussion", ls_param=ls)

def new_post(name, post):
    posts_connection = SQLDatabase("Posts.db")
    posts_connection.add_post(name, post)
    return page_view("valid-post");

def delete_post(id):
    posts_connection = SQLDatabase("Posts.db")
    posts_connection.delete_post(id)

    post_ids = posts_connection.get_all_post_Id()
    post_usernames = posts_connection.get_all_post_name()
    post_contents = posts_connection.get_all_post_content()

    ls = []; i = 0
    while i < len(post_usernames):
        ls.append(post_ids[i][0])
        ls.append(post_usernames[i][0])
        ls.append(post_contents[i][0])
        i+=1

    return page_view("discussion", ls_param=ls)

def friend_list(username):
    users_connection = SQLDatabase("Users.db")
    print(username)
    friendlist = users_connection.get_friends(username)
    print(friendlist)
    if friendlist != None:
        friendlist = friendlist[0].split("/")
    else:
        friendlist = []

    invites = users_connection.get_friendinv(username)
    if invites != None:
        invites = invites[0].split("/")
    else:
        invites = []
    
    return page_view("friend-list", friends=friendlist, inv=invites)

def send_friendreq(username, receiver):
    users_connection = SQLDatabase("Users.db")
    friendlist = users_connection.get_friends(username)
    if friendlist != None:
        friendlist = friendlist[0].split("/")
        for x in range(len(friendlist)):
            if friendlist[x] == receiver:
                reason = "this user is already your friend"
                return page_view("invalid-invite", error=reason)
    
    receiverinv = users_connection.get_friendinv(receiver)
    print(receiverinv)
    if receiverinv != None:
        if receiverinv[0] != '':
            receiverinv = receiverinv[0].split("/")
            
            for x in range(len(receiverinv)):
                if receiverinv[x] == receiver:
                    reason = "this user already has a pending invitation from you"
                    return page_view("invalid-invite", error=reason)
            receiverinv.append(username)
            invitation = "/".join(receiverinv)
        else:
            invitation = username
    else:
        invitation = username
    print(invitation)
    print(username)
    users_connection.add_friendinv(receiver, invitation)
    
    return page_view("friend-list", friends=friendlist)
def accept_friendreq(username):
    users_connection = SQLDatabase("Users.db")
    friendlist = users_connection.get_friends(username)
    if friendlist != None:
        friendlist = friendlist[0].split("/")
    else:
        friendlist = []

    invites = users_connection.get_friendinv(username)
    
    if invites[0] != '':
        invites = invites[0].split("/")
        for y in range(len(invites)):
            friendls = users_connection.get_friends(invites[y])
            if friendlist != None:
                friendls.append(username)
                friendls = "/".join(friendls)
                users_connection.add_friends(invites[y], friendls)
            else:
                friendls = username
                users_connection.add_friends(invites[y], friendls)
        
    else:
        reason = "you have no pending friend invites"
        return page_view("invalid-invite", error=reason)
    friendlist = friendlist + invites
    friendlist = "/".join(friendlist)
    users_connection.add_friends(username, friendlist)
    users_connection.remove_friendinv(username)
    return friend_list(username)
    
def messages():
    return page_view("messages")

def my_message(user_name):
    '''
    stores message, sender name and ivr values to sql database
    '''
    users_connection = SQLDatabase("Users.db")
    exists = users_connection.username_exists(user_name)
    message = users_connection.get_message(user_name)
    sender = users_connection.get_sender(user_name)
    key = users_connection.get_key(sender)
    ivr = users_connection.get_ivr(user_name)
    return page_view("my-message", m=message,k=key,ivr=ivr)
#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords
        :: username :: The username
        :: password :: The password
        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    sleep(0.1)
    users_connection = SQLDatabase("Users.db")
    login = users_connection.check_credentials(username, password)

    if login:
        admin = users_connection.is_admin(username);
        return page_view("valid-login", name=username, admin=admin)
    else:
        err_str = "Username or Password is incorrect"
        return page_view("invalid", reason=err_str)

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)
