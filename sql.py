import sqlite3	
import hashlib	
import secrets	
import base64	
# This class is a simple handler for all of our SQL database actions	
# Practicing a good separation of concerns, we should only ever call 	
# These functions from our models	
ALGORITHM = "pbkdf2_sha256"	
def hash_password(password, salt=None, iterations=260000):	
    if salt is None:	
        salt = secrets.token_hex(16)	
    assert salt and isinstance(salt, str) and "$" not in salt	
    assert isinstance(password, str)	
    pw_hash = hashlib.pbkdf2_hmac(	
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations	
    )	
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()	
    return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)	
def verify_password(password_hash, password):	
    if (password_hash or "").count("$") != 3:	
        return False	
    algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)	
    iterations = int(iterations)	
    assert algorithm == ALGORITHM	
    compare_hash = hash_password(password, salt, iterations)	
    return secrets.compare_digest(password_hash, compare_hash)	

class SQLDatabase():
    '''	
        Our SQL Database	
    '''	
    # Get the database running	
    def __init__(self, database_args):	
        self.conn = sqlite3.connect(database_args)	
        self.cur = self.conn.cursor()	
    # SQLite 3 does not natively support multiple commands in a single statement	
    # Using this handler restores this functionality	
    # This only returns the output of the last command	
    def execute(self, sql_string):	
        out = None	
        for string in sql_string.split(";"):	
            try:	
                out = self.cur.execute(string)	
            except:	
                pass	
        return out	
    # Commit changes to the database	
    def commit(self):	
        self.conn.commit()	
    #-----------------------------------------------------------------------------	
    	
    # Sets up the database	
    # Default admin password	
    def user_database_setup(self, admin_password="Adminadmin1!"):
        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.commit()	
        # Create the users table	
        self.execute("""CREATE TABLE Users(	
            username TEXT,	
            password TEXT,	
            admin INTEGER DEFAULT 0,	
            r_message TEXT,	
            public_key TEXT,	
            sender TEXT,	
            ivr TEXT,
            friends TEXT,
            invites TEXT
        )""")	
        self.commit()

        # Add our admin user	
        hashed_admin_password = hash_password(admin_password)
        self.add_user('admin', admin_password, admin_password, admin=1)

    def post_database_setup(self):
        self.execute("DROP TABLE IF EXISTS Posts")
        self.commit()

        self.execute("""CREATE TABLE Posts (	
            username TEXT,	
            post TEXT	
        )""")
        #self.add_post("user1", "This message is generated from sql.py")
        #self.add_post("sqlborn2", "So is this one")
        #self.add_post("nonexistantperson3", "This font is kind of ugly, but we can change it later")
        self.commit()
        
    #-----------------------------------------------------------------------------
    # User handling	
    #-----------------------------------------------------------------------------
    def add_user(self, username, password, passwordcheck, admin=0):
        create = True
        err_str = ""

        exists = self.username_exists(username)
        if exists:
            err_str = "Username already exists"
            create = False
        elif len(password) < 8:
            err_str = "Password must be at least 10 characters long"
            create = False
        elif (not any(x.isupper() for x in password)
              or not any(x.isupper() for x in password)):
            err_str = "Password must contain: uppercase and lowercase letters, and numbers."
            create = False
        elif password != passwordcheck:
            err_str = "Passwords do not match"
            create = False

        if create:
            sql_cmd = """	
                    INSERT INTO Users	
                    VALUES('{username}', '{password}', {admin}, '{message}', '{public_key}', '{sender}', '{ivr}', '{friends}', '{invites}')	
                """
            hashed_password = hash_password(password)

            sql_cmd = sql_cmd.format(username=username, password=hashed_password, admin=admin, message = "", public_key="", sender="", ivr="", friends="", invites="")
            self.execute(sql_cmd)
            self.commit()

            return "added"
        else:
            return err_str

    def delete_user(self, user_number):
        self.cur.execute("DELETE FROM Users WHERE rowid = ?",(user_number,))
        self.commit()
    def get_all_user_id(self):
        rows = self.cur.execute("SELECT rowid FROM Users").fetchall()
        return rows
    def get_all_username(self):
        rows = self.cur.execute("SELECT username FROM Users").fetchall()
        return rows
    def get_all_user_admins(self):
        rows = self.cur.execute("SELECT admin FROM Users").fetchall()
        return rows
    def give_user_admin_rights(self, user_number):
        self.cur.execute("UPDATE Users SET admin = 1 WHERE rowid = ?",(user_number,))
        self.commit()

    #-----------------------------------------------------------------------------
    # Post Handling
    #-----------------------------------------------------------------------------
    def add_post(self, username, post):
        sql_cmd = """	
                INSERT INTO Posts
                VALUES('{username}', '{post}')	
            """

        post = post.replace("'", "''");
        sql_cmd = sql_cmd.format(username=username, post=post)
        self.execute(sql_cmd)
        self.commit()
        return True
    def delete_post(self, post_number):
        self.cur.execute("DELETE FROM Posts WHERE rowid = ?",(post_number,))
        self.commit()
    def get_all_post_Id(self):
        rows = self.cur.execute("SELECT rowid FROM Posts").fetchall()
        return rows
    def get_all_post_name(self):
        rows = self.cur.execute("SELECT username FROM Posts").fetchall()
        return rows
    def get_all_post_content(self):
        rows = self.cur.execute("SELECT post FROM Posts").fetchall()
        return rows

    #-----------------------------------------------------------------------------	
    # Additional user functions
    def username_exists(self, username):	
        sql_query = """	
                SELECT 1 	
                FROM Users	
                WHERE username = '{username}'	
            """	
        sql_query = sql_query.format(username=username)	
        self.execute(sql_query)	
        if self.cur.fetchone():	
            return True	
        else:	
            return False	
    # Check login credentials	
    def check_credentials(self, username, password):	
        sql_query = """	
                SELECT password 	
                FROM Users	
                WHERE username = '{username}'	
            """

        sql_query = sql_query.format(username=username)	
        user = self.execute(sql_query).fetchone()

        # Check if username exists	
        if user == None:	
            return False	
        # Check if passwords match	
        match = verify_password(user[0], password)	
        if match:	
            return True	
        else:	
            return False

    def is_admin(self, username):
        sql_query = """	
                SELECT admin 	
                FROM Users	
                WHERE username = '{username}'	
            """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        is_admin = float(self.cur.fetchone()[0])

        if is_admin:
            return True
        else:
            return False

    def update_key(self, receiver_name, key):	
        self.cur.execute("UPDATE Users SET public_key = ? WHERE username = ?",(key, receiver_name))	
        self.commit()	
        	
    def get_key(self, name):	
        self.cur.execute("SELECT public_key FROM Users WHERE username = ?",(name,))	
        key = self.cur.fetchone()	
        return key[0]	
    	
    def get_sender(self, name):	
        self.cur.execute("SELECT sender FROM Users WHERE username = ?",(name,))	
        sender = self.cur.fetchone()	
        return sender[0]	
    	
    def get_ivr(self, name):	
        self.cur.execute("SELECT ivr FROM Users WHERE username = ?",(name,))	
        ivr = self.cur.fetchone()	
        return ivr[0]	
    	
    def get_message(self, my_name):	
        self.cur.execute("SELECT r_message FROM Users WHERE username = ?",(my_name,))	
        message = self.cur.fetchone()	
        return message[0]	
    def update_message(self, receiver_name, message, sender, ivr):	
        print("receiver: "+ receiver_name)	
        print("sender: " + sender)	
        print("message: " + message)	
        print("ivr: " + ivr)	
        self.cur.execute("UPDATE Users SET r_message = ? WHERE username = ?",(message, receiver_name))	
        self.cur.execute("UPDATE Users SET sender = ? WHERE username = ?",(sender, receiver_name))	
        self.cur.execute("UPDATE Users SET ivr = ? WHERE username = ?",(ivr, receiver_name))	
        self.commit()	
    #-----------------------------------------------------------------------------
    # Friends handling	
    #-----------------------------------------------------------------------------
    def get_friends(self, username):
        rows = self.cur.execute("SELECT friends FROM Users WHERE username = ?",(username,)).fetchone()
        return rows
    def get_friendinv(self, username):
        rows = self.cur.execute("SELECT invites FROM Users WHERE username = ?",(username,)).fetchone()
        return rows
    def add_friendinv(self, username, invite):
        
        rows = self.cur.execute("UPDATE Users SET invites = ? WHERE username = ?",(invite, username))
        self.commit()
    def remove_friendinv(self, username):
        
        rows = self.cur.execute("DELETE FROM Users WHERE username = ?",(username),)
        self.commit()
    def add_friends(self, username, friend):
        
        rows = self.cur.execute("UPDATE Users SET friends = ? WHERE username = ?",(friend, username))
        self.commit()
