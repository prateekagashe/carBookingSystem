from flask import Flask
from flaskext.mysql import MySQL

db = 'k'
app = Flask(__name__)
app.secret_key = 'aheexbeeuqo299ee29'
app.config['SESSION_KEY'] = 'Filesystem'

mysql = MySQL()

 
# MySQL configurations
config = { 
	'user' : 'b7ab09a75ef978',
	'password' : 'c6286954',
	'database' : 'heroku_ff5dabd9118e154',
	'host' : 'us-cdbr-iron-east-04.cleardb.net',
}
mysql.init_app(app)
