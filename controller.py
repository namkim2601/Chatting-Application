
'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request, static_file

import model

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures
        Serves images from static/img/
        :: picture :: A path to the requested picture
        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css
        Serves css from static/css/
        :: css :: A path to the requested css
        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        Serves js from static/js/
        :: js :: A path to the requested javascript
        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Display the login page first
@get('/')
@get('/login')
def get_login_controller():
    '''
        Serves the login page
    '''
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''

    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')

    # Call the appropriate method
    return model.login_check(username, password)

@get('/profile')
def get_profile():
    '''
        Serves the home page
    '''
    return model.profile()

@get('/admin-page')
def get_admin_page():

    return model.admin_page()

@post("/admin-page-add-user")
def admin_page_add_user():
    username = request.forms.get('username')
    password = request.forms.get('password')

    return model.admin_page_add_user(username, password)

@post("/delete-user")
def delete_user():
    user_id = request.forms.get('id')

    return model.delete_user(user_id)

@post("/give-admin-rights")
def give_user_admin_rights():
    user_id = request.forms.get('id')

    return model.give_user_admin_rights(user_id)

@get('/create-account')
def get_create_account():
    '''
        Serves the create account page
    '''
    return model.create_account_form()

@post('/create-account')
def post_create_account():
    '''
        handles account creation
    '''

    username = request.forms.get('username')
    password = request.forms.get('password')
    passwordCheck = request.forms.get('passwordCheck')

    return model.create_account(username, password, passwordCheck)

@post('/account-key')
def change_account_key():
    '''
        handles public key storage upon account creation
    '''
    username = request.forms.get('username')
    public_key = request.forms.get('public_key')

    return model.change_account_key(username, public_key)

@post('/get-dh')
def post_get_dh():
    '''
        retrieves public key of another user upon account request
    '''
    username = request.forms.get('username')
    message = request.forms.get('message')
    sender = request.forms.get('sender')
    return model.get_dh_key(username,message,sender)
@post('/send-message')
def post_send_message():
    '''
        stores message sent to another user upon account request
    '''
    username = request.forms.get('username')
    message = request.forms.get('message')
    sender = request.forms.get('sender')
    ivr = request.forms.get('ivr')
    return model.send_message(username, message, sender, ivr)

@get('/friend-list')
def friend_list():
    username = request.forms.get('username')
    
    return model.friend_list(username)

@post('/send-friendreq')
def friend_list():
    username = request.forms.get('username')
    receiver = request.forms.get('receiver')

    return model.send_friendreq(username, receiver)

@post('/accept-invites')
def friend_list():
    username = request.forms.get('n')

    return model.accept_friendreq(username)

@get('/messages')
def messages():
    '''
        handles user page that became available after login
    '''
    return model.messages()
@post('/display_friends')
def display():
    username = request.forms.get('name')
    print(username)
    return model.friend_list(username)
@post('/my-messages')
def messages():
    '''
        presents user message page after they clicked the corresbonding button in user page
    '''

    name = request.forms.get('name')
    return model.my_message(name)
@get('/discussion')
def discussion():
    return model.discussion()

@post('/delete-post')
def delete_post():
    post_id = request.forms.get('id');

    return model.delete_post(post_id)

@post('/discussion')
def post_forum():
    username = request.forms.get('username')
    post = request.forms.get('content')

    return model.new_post(username, post)
#-----------------------------------------------------------------------------
@get('/about')
def get_about():
    '''
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)
'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''
