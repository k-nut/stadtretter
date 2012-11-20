import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
                  abort, render_template, flash, jsonify, json
import urllib, urllib2, simplejson
import datetime

# configuration
DATABASE = './flaskr.db'
DEBUG = True
SECRET_KEY = 'supersecret'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/get-markers/<south>/<north>/<west>/<east>")
def markers(south, north, west, east):
  q = g.db.execute('select id, name, title, picture, lat, lon from entries where lat between %f and %f and lon between %f and %f order by id desc limit 50 '%(float(south), float(north), float(west), float(east)))
  return jsonify(marker=[dict(id=row[0], name=row[1], title=row[2], picture=row[3], lat=row[4], lon=row[5]) for row in q.fetchall()])

@app.route('/add', methods=['POST'])
def add_entry():
    g.db.execute('insert into entries (pubdate, name, title, picture, lat, lon) values (?, ?, ?, ?, ?, ?)',
                 [datetime.date.today(), request.form['name'], request.form['title'], request.form['picture'], request.form['lat'], request.form['lon']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('home'))

@app.route("/getCoordinates/<query>")
def findaddress(query):
    url = "http://nominatim.openstreetmap.org/search/%s"%(query)
    data = urllib.urlencode({"format": "json"})
    f = urllib2.urlopen(url + "?" + data)
    result = f.read()
    best_match = json.loads(result)[0]
    re = {"lat":best_match["lat"], "lon":best_match["lon"]}
    return jsonify(lat=best_match["lat"], lon=best_match["lon"]) 

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()



def connect_db():
        return sqlite3.connect(app.config['DATABASE'])



if __name__=="__main__":
    app.debug = True
    app.run()
