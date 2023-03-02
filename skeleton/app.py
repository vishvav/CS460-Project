######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import datetime

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

def getUserIdList():
    cursor = conn.cursor()
    cursor.execute("SELECT user_id from Users")
    return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user


@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/registeruser'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/registeruser", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/registeruser", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		fname=request.form.get('fname')
		lname=request.form.get('lname')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
		dob=request.form.get('dob')
	except Exception as e:
		print(e)
		print("couldn't find all tokens - Error 1") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('registeruser'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	print(test)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, fname, lname, hometown, gender, dob) VALUES ('{0}','{1}','{2}','{3}','{4}', '{5}','{6}')".format(email, password, fname, lname, hometown, gender, dob)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		user.name = (fname + " " + lname)
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens - Error 2") #changed for debugging
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, photo_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Albums WHERE user_id = '{0}'".format(uid))
	result = [[col.encode("utf8") if isinstance(col, str) else col for col in row] for row in cursor.fetchall()]
	result = [x[0] for x in result]
	return result

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def getAlbumPhotos(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT p.data, a.name, p.caption, p.photo_id from photos p, albums a \
    		WHERE a.user_id = '{0}' AND a.name = '{1}' AND p.album_id = a.album_id".format(uid, name))
	return cursor.fetchall() 	

def getTagId(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_id FROM Tags WHERE tag = '{0}'".format(tag))
	return cursor.fetchone()[0]

def getTaggedPhotos(uid):  ##might need to edit this to make list
	cursor = conn.cursor() 
	cursor.execute("SELECT p.data, p.caption, p.photo_id FROM Photos p, Tags t, TaggedPhotos tp \
		WHERE t.user_id = '{0}' AND tp.tag_id = t.tag_id AND tp.photo_id = p.photo_id".format(uid))
	return cursor.fetchall()

def getAlbumId(name):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE album_name = '{0}'".format(name))
	return cursor.fetchall()[0]

def getHomeTown(uid):
	cursor = conn.cursor()
	cursor.execute("Select hometown From Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getDob(uid):
	cursor = conn.cursor()
	cursor.execute("Select dob from Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getGender(uid):
	cursor = conn.cursor()
	cursor.execute("Select gender From Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getfName(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT fname FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getlName(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT lname FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def getUserPID(imgdata):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users WHERE imgdata = '{0}'".format(imgdata))
	return cursor.fetchone()[0]


#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	print(uid)
	return render_template('profile.html', name=flask_login.current_user.id, message="Here is your profile", hometown=getHomeTown(uid), dob=getDob(uid),  gender=getGender(uid), fName=getfName(uid), lastName=getlName(uid), photos = getUsersPhotos(uid))


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tag = request.form.get('tag')
		album_name = request.form.get('album_name')
		aid = getAlbumId(album_name)
		photo_data =imgfile.read()
		cursor = conn.cursor()
		
		cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s)",(photo_data, uid, caption, aid))
		conn.commit()
		return render_template('photo_feed.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid))
	return render_template('upload.html', message='Upload a photo')


	"""
	cursor.execute("SELECT album_name FROM Albums WHERE user_id = '{0}'".format(uid))
	albums = cursor.fetchall()
	temp = 0
	for i in range(len(albums)):
		if albums[i][0] == album_name:
			temp += 1
	if temp == 0:
		return render_template('upload.html', message = 'Album does not exist, do not forget to create it first!')
	cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s)",(photo_data, uid, caption))
	conn.commit()

	photo_id = cursor.lastrowid
	cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}' AND album_name = '{1}'".format(uid, album_name))
	album_id = cursor.fetchone()[0]
	cursor.execute("INSERT INTO StoredIn(photo_id, album_id) VALUES ('{0}', '{1}')".format(photo_id, album_id))
	conn.commit()

	split_tag = tag.split()
	cursor = conn.cursor()

	for i in range(len(split_tag)):
		cursor.execute("INSERT INTO Tags(tag) VALUES ('{0}')".format(split_tag[i]))
		conn.commit()
		tag_id = cursor.lastrowid
		cursor.execute("INSERT INTO TaggedPhotos(photo_id, tag_id) VALUES ('{0}', '{1}')".format(photo_id, tag_id))
		conn.commit()
	return render_template('view_photos.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid))

return render_template('upload.html')"""
		
#end photo uploading code

#begin tags code

@app.route('/tags', methods=['GET', 'POST'])
def search_tag():
	if request.method == 'POST':
		tag = request.form.get('tag')
		all_tags = tag.split()
		return render_template('tags.html', message='Here are the photos with the tag:', photos=getTaggedPhotos(all_tags))
	
	return render_template('tags.html')
#end tags code

#being photos code
@app.route('/photos', methods=['GET', 'POST'])
def comment():
	if getUserIdFromEmail(flask_login.current_user.id) is None:
		uid = 0
		name = 'Guest'
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		user_photo_id = request.form.get('user_id')
		user_photo_id = int(user_photo_id)

		if uid - user_photo_id == 0:
			return render_template('hello.html', message='You cannot comment on your own photos', user=uid, photos=getUsersPhotos(uid))
		else:
			photo_id = request.form.get('photo_id')
			comment = request.form.get('comment')
			date = datetime.datetime.now().date()
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Comments(user_id, date, comment, photo_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(uid, date, comment, photo_id))
			conn.commit()
			comment_id = cursor.lastrowid

			cursor.execute("INSERT INTO CommentedOn(comment_id, photo_id) VALUES ('{0}', '{1}')".format(comment_id, photo_id))
			conn.commit()
			return render_template('hello.html', message='Comment added!', user=uid, photos=allPictures(uid))

	return render_template('hello.html', message='You are viewing recent photos', user=uid, photos=allPictures(uid)) #maybe change to getAllPhotos()/allpictures

#end photos code
def recentUserPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT p.imgdata, p.photo_id, p.caption, u.fname, u.lname, p.user_id FROM Pictures p, Users u WHERE p.user_id = u.user_id AND p.user_id = '{0}' ORDER BY p.photo_id DESC".format(uid))
	return cursor.fetchall()

#begin photo viewing code
@app.route('/photo_feed', methods=['GET', 'POST']) #see photos
@flask_login.login_required


def photoFeed():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		photo_id = request.form.get('photo_id')
		deletePhoto(photo_id)
		return render_template('photo_feed.html', name=flask_login.current_user.id, user= uid,message='Here are your photos', photos=recentUserPhotos(uid))

	return render_template('photo_feed.html', name=flask_login.current_user.id, message='Here are your photos', photos=recentUserPhotos(uid))

def deletePhoto(photo_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Likes WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

	cursor.execute("SELECT comment_id FROM CommentedOn WHERE photo_id = '{0}'".format(photo_id))
	comments = cursor.fetchall()

	cursor.execute("DELETE FROM CommentedOn WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

	for i in range(len(comments)):
		cursor.execute("DELETE FROM Comments WHERE comment_id = '{0}'".format(comments[i][0]))
		conn.commit()
	cursor.execute("SELECT tag_id FROM TaggedPhotos WHERE photo_id = '{0}'".format(photo_id))
	tags = cursor.fetchall()

	cursor.execute("DELETE FROM TaggedPhotos WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

	for i in range(len(tags)):
		cursor.execute("DELETE FROM Tags WHERE tag_id = '{0}'".format(tags[i][0]))
		conn.commit()
	
	cursor.execute("DELETE FROM Pictures WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

	cursor.execute("DELETE FROM Tags WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

def getComments(photo_id):  ##double check this
	cursor = conn.cursor()
	cursor.execute("SELECT c.comment_id, c.comment, c.date, u.fname, u.lname, c.user_id FROM Comments c, Users u WHERE c.user_id = u.user_id AND c.photo_id = '{0}'".format(photo_id))
	return cursor.fetchall()

def getLikes(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT u.fname, u.lname, u.user_id FROM Likes l, Users u WHERE l.user_id = u.user_id AND l.photo_id = '{0}'".format(photo_id))
	return cursor.fetchall()

def getTags(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT t.tag FROM Tags t, TaggedPhotos tp WHERE t.tag_id = tp.tag_id AND tp.photo_id = '{0}'".format(photo_id))
	return cursor.fetchall()



def allPictures():
	cursor = conn.cursor()
	cursor.execute("SELECT p.imgdata, p.photo_id, p.caption, u.fname, u.lname, p.user_id FROM Pictures p, Users u WHERE p.user_id = u.user_id ORDER BY p.photo_id DESC")
	pictures = cursor.fetchall()
	
	full_list = []
	for i in range(len(pictures)):
		photos_list = []
		id = int(pictures[i][1])
		for j in range(len(pictures[i])):
			x = [pictures[i][j]]
			photos_list.append(x)
		
		comments = getComments(id)
		comments_list = []

		for k in range(len(comments)):
			comments.append(comments[k])

		photos_list.append(comments)

		likes = getLikes(id)
		likes_list = []
		for m in range(len(likes)):
			likes_list.append(likes[m])

		photos_list.append(likes_list)

		tags = getTags(id)
		tags_list = []
		for n in range(len(tags)):
			tags_list.append(tags[n])
		
		photos_list.append(tags_list)

		full_list.append(photos_list)

	return full_list

@app.route('/see_likes')
def seeLikes():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)

		photo_id = request.form.get('photo_id')
		num_of_likes = getLikes(photo_id)
		if num_of_likes>0:
			cursor = conn.cursor()
			cursor.execute("SELECT u.fname, u.lname, u.user_id FROM Likes l, Users u WHERE l.user_id = u.user_id AND l.photo_id = '{0}'".format(photo_id))
			users = cursor.fetchall()
			return render_template('see_likes.html', message='Here are the users who liked this photo:', names=users)
	return render_template('hello.html', name=flask_login.current_user.id, message='Here are your photos', photos=recentUserPhotos(uid))


@app.route('/find_friends', methods=['GET', 'POST'])
@flask_login.login_required
def findFriends():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		email = request.form.get('email')
		cursor = conn.cursor()
		cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(email))
		user_id2 = cursor.fetchone()[0]

		cursor.execute("SELECT user_id2 FROM Friends WHERE user_id1 = '{0}'" .format(uid))
		friends = cursor.fetchall()
		f_list = []
		for i in range(len(friends)):
			if user_id2 == friends[i]:
				return render_template('find_friends.html', name=flask_login.current_user.id, message='You are already friends with this user!')
		return render_template('find_friends_result.html', name=flask_login.current_user.id, message='Here are the results of your search:', friends=lookupFriend(email))

	return render_template('find_friends.html')

def lookupFriend(email):
	cursor = conn.cursor()
	cursor.execute("SELECT fname, lname, email FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchall()


@app.route('/find_friends_result', methods=['GET', 'POST'])
@flask_login.login_required
def findFriendsResult():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flash_login.current_user.id)
		f_id = request.form.get('friend_id')
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(uid, f_id))
		conn.commit()
		return render_template('find_friends.html', name=flask_login.current_user.id, message='You are now friends with this user!')
	return render_template('find_friends_result.html')

@app.route('/friends_list', methods=['GET'])
@flask_login.login_required
def friendsList():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('friends_list.html', name=flask_login.current_user.id, message='Here are your friends:', friends=allFriends(uid))

def allFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT u.fname, u.lname, u.email FROM Users u, Friends f WHERE u.user_id = f.user_id2 AND f.user_id1 = '{0}'".format(uid))
	return cursor.fetchall()

@app.route('/make_album', methods=['GET', 'POST'])
@flask_login.login_required
def makeAlbum():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		album_name = request.form.get('album_name')
		date_of_creation = datetime.datetime.now()
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums (album_name, user_id, date_of_creation) VALUES ('{0}', '{1}', '{2}')".format(album_name, uid, date_of_creation))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='You have successfully created an album!', photos=recentUserPhotos(uid))
	return render_template('make_album.html')


@app.route('/like', methods=['GET', 'POST'])
@flask_login.login_required
def like():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		photo_id = request.form.get('photo_id')
		photo_id = int(photo_id)
		cursor = conn.cursor()
		cursor.execute("SELECT photo_id FROM Likes WHERE user_id = '{0}'".format(uid))
		liked_photos = cursor.fetchall()
		for i in range(len(liked_photos)):
			if photo_id == int(liked_photos[i][0]):
				return render_template('hello.html', name=flask_login.current_user.id, message='You already liked this photo!', photos=allPictures(uid))
		cursor.execute("INSERT INTO Likes (user_id, photo_id) VALUES ('{0}', '{1}')".format(uid, photo_id))
		conn.commit()

		return render_template('hello.html', name=flask_login.current_user.id, message='You liked this photo!', photos=allPictures(uid))
	return render_template('hello.html', message='Most recent photos',user=uid, photos=allPictures())


@app.route('/albums', methods=['GET', 'POST'])
@flask_login.login_required
def albums():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		return render_template('albums.html', name=flask_login.current_user.id, message='Here are your albums:', albums=allAlbums(uid))
	return render_template('albums.html', name=flask_login.current_user.id, message='Here are your albums:', albums=allAlbums(uid))

def allAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT a.album_name, COUNT(s.photo_id), a.album_id FROM Albums a, StoredIn s WHERE a.album_id = s.album_id AND a.user_id = '{0}' GROUP BY a.album_name, a.album_id".format(uid)) #double check
	return cursor.fetchall()

@app.route('/see_photos', methods=['GET', 'POST'])
@flask_login.login_required
def seePhotos():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		album_name = request.form.get('album_name')
		cursor = conn.cursor()
		cursor.execute("SELECT p.imgdata, p.photo_id, p.caption FROM Pictures p, Albums a, StoredIn s WHERE a.album_id = s.album_id AND s.photo_id = p.photo_id AND a.album_name = '{0}' AND a.user_id = '{1}'".format(album_name, uid))
		photos = cursor.fetchall()
		return render_template('photo_feed.html', name=flask_login.current_user.id, message='Here are the photos in this album:', photos=photos)
	return render_template('albums.html')

@app.route('/delete_album', methods=['GET', 'POST'])
@flask_login.login_required
def deleteAlbum():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		album_id = request.form.get('album_id')
		cursor = conn.cursor()

		cursor.execute("SELECT photo_id FROM StoredIn WHERE album_id = '{0}'".format(album_id))
		photos = cursor.fetchall()

		for i in range(len(photos)):
			deletePhoto(int(photos[i][0]))
		cursor.execute("DELETE FROM Albums WHERE album_id = '{0}'".format(album_id))
		conn.commit()

		return render_template('albums.html', name=flask_login.current_user.id, message='You have successfully deleted this album!', albums=allAlbums(uid))
	return render_template('albums.html', name=flask_login.current_user.id, message='Here are your albums:', albums=allAlbums(uid))

@app.route('/most_popular_tags', methods=['GET', 'POST'])
def mostPopularTags():
	if request.method == 'POST':
		tag = request.form.get('tag')
		cursor = conn.cursor()
		cursor.execute("SELECT p.imgdata, t.tag, p.caption, u.fname, u.lname FROM Users u, Pictures p, TaggedPhotos tp, Tags t WHERE u.user_id = p.user_id AND p.photo_id = tp.photo_id AND tp.tag_id = t.tag_id AND t.tag = '{0}'".format(tag))
		tagss = cursor.fetchall()

		return render_template('tags.html', name=flask_login.current_user.id, message='Here are the photos with this tag:', photos=tagss)
	return render_template('most_popular_tags.html', tags=topThreeTags())

def topThreeTags():
	cursor = conn.cursor()
	cursor.execute("SELECT t.tag, COUNT(t.tag) FROM Tags t, TaggedPhotos tp WHERE t.tag_id = tp.tag_id GROUP BY t.tag ORDER BY COUNT(t.tag) DESC LIMIT 3")
	return cursor.fetchall()

@app.route('/reccomended_friends', methods=['GET', 'POST'])
@flask_login.login_required
def reccomendedFriends():
	"""NOT IMPLEMENTED"""

@app.route('/reccomended_photos', methods=['GET', 'POST'])
@flask_login.login_required
def reccomendedPhotos():
	"""NOT IMPLEMENTED"""



if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
