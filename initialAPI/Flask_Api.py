#Student: Animesh Chaudhry
#Project 1
#Class: CPSC476

import click
import flask
from flask import request, jsonify, Response, g
from functools import wraps 
import sqlite3
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Instructions (Initialize the schema in the database):
# export FLASK_APP=Flask_Api
# python3
# >> from Flask_Api import init_db
# >> init_db()
#Note: Initial schema procedure taken from: http://flask.pocoo.org/docs/1.0/patterns/sqlite3/#initial-schemas
@app.cli.command()
def init_db():
    with app.app_context():
        db = sqlite3.connect('test.db')
        with app.open_resource('init.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

##Authorization Decorator
def auth_req(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        auth = request.authorization

        conn = sqlite3.connect('test.db')
        cur = conn.cursor()
        query = 'SELECT * FROM Users'
        results = cur.execute(query).fetchall()

        for i in range(len(results)):
            if auth and auth.username == results[i][1] and auth.password == results[i][2]:
                conn.close()
                return f(results[i][0], *args, **kwargs)  
        conn.close()
        return Response('Wrong Credentials', 401, {'WWW-Authenticate': 'Basic realm ="Login Required"'})

    return decorate 


# This function returns items from the database     
# as dictionaries instead of lists (Better for outputting to JSON)
# Procedure taken from the programming historian website: https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/', methods=['GET'])
@auth_req
def root(usr_id):
    return jsonify({'ID of Logged in User': usr_id})

@app.route('/allforums', methods=['GET'])
def api_all():
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_forums = cur.execute('SELECT * FROM Discussion_Forum;').fetchall()

    return jsonify(all_forums)

###########################################...COMPLETE...#########################################3
# Method: GET
# URL: /forums
# Action: List available discussion forums
# Request Payload: None
# Successful Response: 
#                      HTTP 200 OK
#                      [
#                         { "id": 1, name: "redis", creator: "alice" },
#                         { "id": 2, name: "mongodb", creator: "bob" }
#                      ]
# Need to list Forum id, Forum name, and the forum creator
# Error Response: None. Returns an empty array if no forums have been created.
# Requires Authentication: No 
@app.route('/forums', methods=['GET'])
def get_Forms():
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    results = cur.execute("SELECT Users.User_Name, Users.ID, Discussion_Forum.id, Discussion_Forum.Forum_Name FROM Users, Discussion_Forum WHERE Discussion_Forum.User_ID = Users.ID").fetchall()
    lst = list()
    for i in range(len(results)):
        lst.append({'id': results[i][2], 'name': results[i][3], 'creator': results[i][0]})
    conn.close()
    return jsonify(lst)


##########################################....COMPLETE....#############################################
# Method: POST
# URL: /forums
# Action: Create a new discussion forum
# Request Payload: Yes
# Ex: {
#       "name": "cassandra"
#     }
# Successful Response: HTTP 201 Created and Location header field set to /forums/<forum_id> for new forum
# Error Response: HTTP 409 Conflict if forum already exists
# Requires Authentication: Yes
# Notes: Forum’s creator is the current authenticated user.
@app.route('/forums', methods=['POST'])
@auth_req
def submit_forum(usr_id):


    conn = sqlite3.connect('test.db')
    #conn.row_factory = dict_factory
    cur = conn.cursor()

    attribute = request.get_json(force=True).get('name')
    jsn_payload = {"name":attribute}

    results = cur.execute("SELECT Forum_Name FROM Discussion_Forum WHERE Forum_Name = :Forum_Name", {'Forum_Name': attribute}).fetchall()

    #Check to see if the forum already exists
    if(len(results) == 1):     
        return "<h1>409</h1><p>Forum Already Exists</p>", 409

    #response = jsonify()
    cur.execute("INSERT INTO Discussion_Forum(Forum_Name,User_ID) VALUES (:Forum_Name, :User_ID)", {'Forum_Name': attribute, 'User_ID': usr_id})
    conn.commit()
    forum = (cur.execute("SELECT id FROM Discussion_Forum ORDER BY ID DESC LIMIT 1;").fetchall())[0][0]
    conn.close()
    response = Response(status=201, mimetype='application/json')
    response.headers['Location'] = "forums/%s" % str(forum) #header field set to /forums/<forum_id> for new forum
    
    
    return response

##########################################....COMPLETE....#############################################
# Method GET
# URL: /forums/<forum_id>
# Action: List threads in the specified forum
# Request Payload: None
# Successful response ex: [
#   {
#     "id": 1,
#     "title": "Does anyone know how to start Redis?",
#     "creator": "bob",
#     "timestamp": "Wed, 05 Sep 2018 16:22:29 GMT"
#   },
#   {
#     "id": 2,
#     "title": "Has anyone heard of Edis?",
#     "creator": "charlie",
#     "timestamp": "Tue, 04 Sep 2018 13:18:43 GMT"
#   }
# ]
# Error Response: HTTP 404 Not Found
# Authentication: No
# Notes: The timestamp for a thread is the timestamp for the most recent post to that thread.
#        The creator for a thread is the author of its first post.
#        Threads are listed in reverse chronological order.
@app.route('/forums/<int:forum_id>', methods=['GET'])
def list_threads(forum_id):
    
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()

    forum_ext = cur.execute("SELECT id FROM Discussion_Forum WHERE Discussion_Forum.id == :forum_id", {'forum_id': forum_id}).fetchall()

    if(len(forum_ext) == 0):
        return "<h1>404</h1><p>Forum Does not exist</p>", 404

    results = cur.execute("SELECT * FROM Threads, Users WHERE Threads.User_ID = Users.ID AND Threads.Forum_ID = :Forum_ID", {'Forum_ID': forum_id}).fetchall()
    lst = list()
    for i in range(len(results)):
        lst.append({'id': results[i][1], 'title': results[i][4], 'creator': results[i][6], 'timestamp': results[i][3]})
    if(len(lst) == 0):
        return "<h1>404</h1><p>Page Not Found, There are no threads in this forum. You can be the first one to create a thread in the forum!</p>", 404

    conn.close()
    return jsonify(lst[::-1])


############################################...COMPLETE...#############################################
# Method: POST
# URL: /forums/<forum_id>
# Action: Create a new thread in the specified forum
# Request Payload: {
#   "title": "Does anyone know how to start MongoDB?",
#   "text": "I'm trying to connect to MongoDB, but it doesn't seem to be running."
#    }
# Successful Response: HTTP 201 Created, Location header field set to /forums/<forum_id>/<thread_id> for new thread.
# Error Response: HTTP 404 Not Found
# Requires Authentication: Yes
# Notes: The text field becomes the first post to the thread. The first post’s author is the current authenticated user.    
@app.route('/forums/<forum_id>', methods=['POST'])
@auth_req
def create_threads(usr_id, forum_id):
    
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()

    title = request.get_json(force=True).get('title')
    text = request.get_json(force=True).get('text')
    jsn_payload = {"title":title, "text": text}

    val_forum = cur.execute("SELECT id FROM Discussion_Forum WHERE id = :forum_id",{'forum_id':forum_id}).fetchall()
    if(len(val_forum) == 0):
        return "<h1>404</h1><p>Forum Not Found</p>", 404


    response = jsonify()
    cur.execute("INSERT INTO Threads(Forum_ID, User_ID, Title) VALUES (:Forum_ID, :User_ID, :Title)", {'Forum_ID': forum_id, 'User_ID': usr_id, 'Title': title})
    conn.commit()
    thread_id = []
    thread_id = (cur.execute("SELECT Thread_ID FROM Threads ORDER BY Thread_ID DESC LIMIT 1;").fetchall())[0][0] 
    cur.execute("INSERT INTO Thread_Posts(Thread_ID, Text_V, User_ID) VALUES (:Thread_ID, :Text_V, :User_ID)", {'Thread_ID': thread_id, 'Text_V': text, 'User_ID': usr_id})
    conn.commit()
    conn.close()
    response = Response(status=201, mimetype='application/json')
    response.headers['Location'] = "forums/%s/%s" % (str(forum_id), str(thread_id)) #header field set to /forums/<forum_id>/<thread_id> 
    
    return response

##########################################...COMPLETE...#################################################################
# Method: GET 
# URL: /forums/<forum_id>/<thread_id>
# Action: List posts to the specified thread
# Request Payload: N/A
# Successful response: HTTP 200 OK
#[
# {
#    "author": "bob",
#   "text": "I'm trying to connect to MongoDB, but it doesn't seem to be running.",
#    "timestamp": "Tue, 04 Sep 2018 15:42:28 GMT"
#  },
#  {
#    "author": "alice",
#    "text": "Ummm… maybe 'sudo service start mongodb'?",
#    "timestamp”: "Tue, 04 Sep 2018 15:45:36 GMT"
#  }
#]
# Error Response: HTTP 404 Not Found
# Requires Authentication: No
# Notes: Posts are listed in chronological order.
@app.route('/forums/<int:forum_id>/<int:thread_id>', methods=['GET'])
def list_threads_posts(forum_id, thread_id):
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    forum_ext =  cur.execute("SELECT Thread_Posts.Thread_ID, Users.User_Name, Thread_Posts.Text_v, Threads.TimeStamp FROM Discussion_Forum, Users, Thread_Posts, Threads WHERE Discussion_Forum.id = :forum_id AND Threads.Thread_ID = :thread_id AND Thread_Posts.User_ID = Users.ID;", {'forum_id': forum_id, 'thread_id': thread_id}).fetchall()
    lst = list()
    #print(forum_ext)

    for i in range(len(forum_ext)):
        if(forum_ext[i][0] == thread_id):
            lst.append({'author': forum_ext[i][1], 'text': forum_ext[i][2], 'timestamp': forum_ext[i][3]})
    if(len(lst) == 0):
        return "<h1>404</h1><p>Page Not Found</p>", 404
    
    conn.close()
    return jsonify(lst)

########################################...COMPLETE...#######################################################
# Method: POST
# URL: /forums/<forum_id>/<thread_id>
# Action: Add a new post to the specified thread
# Request Payload: {
#                      "text": "@Bob: Derp."
#                  }
# Successful Response: HTTP 201 Created
# Error Response: HTTP 404 Not Found
# Requires Authentication: Yes
# Notes: The post’s author is the current authenticated user.
@app.route('/forums/<int:forum_id>/<int:thread_id>', methods=['POST'])
@auth_req
def add_post(usr_id, forum_id, thread_id):
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()

    text_v = request.get_json(force=True).get('text')
    forum_ext =  cur.execute("SELECT Thread_Posts.Thread_ID, Users.User_Name, Thread_Posts.Text_v, Threads.TimeStamp FROM Discussion_Forum, Users, Thread_Posts, Threads WHERE Discussion_Forum.id = :forum_id AND Threads.Thread_ID = :thread_id AND Thread_Posts.User_ID = Users.ID;", {'forum_id': forum_id, 'thread_id': thread_id}).fetchall()
    lst = list()
    #print(forum_ext)

    for i in range(len(forum_ext)):
        if(forum_ext[i][0] == thread_id):
            lst.append({'author': forum_ext[i][1], 'text': forum_ext[i][2], 'timestamp': forum_ext[i][3]})
    if(len(lst) == 0):
        return "<h1>404</h1><p>Page Not Found</p>", 404
    jsn_payload = {"text": text_v}
    cur.execute("INSERT INTO Thread_Posts(Text_V, Thread_ID, User_ID) VALUES(:text_v, :thread_id, :usr_id);", {'text_v': text_v, 'thread_id':thread_id, 'usr_id':usr_id})
    conn.commit()
    conn.close()

    return jsonify(jsn_payload)

#####################################...COMPLETE...#######################################
# Method: POST
# URL: /users
# Action: Create a new user
# Request Payload: 
#                   {
#                       "username": "eve",
#                       "password”: "passw0rd"
#                   }
# Successful Response: HTTP 201 Created
# Error Response: HTTP 409 Conflict if username already exists  
# Requires Authentication: No
@app.route('/users', methods=['POST'])
def Create_User():
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()

    username = request.get_json(force=True).get('username')
    password_sec = request.get_json(force=True).get('password')

    jsn_payload = {"username": username, "password": password_sec}

    names = cur.execute("SELECT User_Name FROM Users").fetchall()

    for i in range(len(names)):
        if(names[i][0] == username):
            return "<h1>409</h1><p>Username already exists</p>", 409
    cur.execute("INSERT INTO Users(User_Name, Password) values(:username, :password_sec);", {'username': username, 'password_sec':password_sec})
    conn.commit()
    conn.close()
    return jsonify(jsn_payload), 201

# Method: PUT
# URL: /users/<username>
# Action: Changes a user’s password
# Request Payload: { 
#                      "username": "eve",
#                      "password": "s3cr3t"
#                  }
# Successful Response: HTTP 200 OK
# Error Response: HTTP 404 Not Found if username does not exist, HTTP 409 Conflict if username does not match the current authenticated user
# Requires Authentication: Yes
@app.route('/users/<string:username>', methods=['PUT'])
@auth_req
def change_psswrd(usr_id, username):
    
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    username = str(request.get_json(force=True).get('username'))
    password_sec = request.get_json(force=True).get('password')

    jsn_payload = {"username": username, "password": password_sec}

    names = cur.execute("SELECT User_Name FROM Users WHERE Users.ID = :usr_id", {'usr_id': usr_id}).fetchall()
    if(len(names) != 1):
        return "<h1>409</h1><p>Authentication Error</p>", 409
    current_login = cur.execute("SELECT User_Name FROM Users WHERE User_Name = :username", {'username': username}).fetchall()
    if(len(current_login) == 0):
        return "<h1>404</h1><p>User Not Found</p>", 409

    cur.execute("UPDATE Users SET User_Password = ? WHERE ID = ?;", (password_sec, usr_id))

    conn.commit()
    conn.close()

    return jsonify(jsn_payload)



@app.errorhandler(404)
def error_404(e):
    return "<h1>404</h1><p>Page Not Found</p>", 404


if __name__ == '__main__': 
    app.run(debug=True)

