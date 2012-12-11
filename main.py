import sqlite3
from flask import Flask, request, g, redirect, url_for, \
        abort, render_template, jsonify, json
import urllib, urllib2
import datetime
from werkzeug import secure_filename
import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('stadtretter.cfg', silent=False)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    ''' Render the main page '''
    return render_template("index.html")

@app.route("/get-markers/<south>/<north>/<west>/<east>")
def markers(south, north, west, east):
    ''' Get all the markers within a bounding box '''
    query = g.db.execute('select id, name, title, picture, lat, lon from entries where lat between %f and %f and lon between %f and %f order by id desc limit 50 '%(float(south), float(north), float(west), float(east)))
    return jsonify(marker=[dict(id=row[0], name=row[1], title=row[2], picture="/static/user-images/"+row[3] if row[3] else "", lat=row[4], lon=row[5]) for row in query.fetchall()])

@app.route('/add', methods=['POST'])
def add_entry():
    ''' Add a new marker to the db '''
    userfile = request.files["picture"]
    if userfile and allowed_file(userfile.filename):
        filename = secure_filename(userfile.filename)
        userfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = ""
    g.db.execute('insert into entries (pubdate, name, title, picture, lat, lon) values (?, ?, ?, ?, ?, ?)',
            [datetime.date.today(), request.form['name'], request.form['title'], filename, request.form['lat'], request.form['lon']])
    g.db.commit()
    return redirect(url_for('home'))

@app.route("/getCoordinates/<query>")
def findaddress(query):
    ''' Call the osm nominatim server to get the coordinates for a query '''
    query = unicode(query).encode("utf-8")
    url = "http://nominatim.openstreetmap.org/search/%s"% (query)
    data = urllib.urlencode({"format": "json"})
    nominatim = urllib2.urlopen(url + "?" + data)
    result = nominatim.read()
    if result != "[]": # if we get something from nominatim return it
        best_match = json.loads(result)[0]
        return jsonify(lat=best_match["lat"], lon=best_match["lon"])
    else: # if not we just return empty brackets
        return jsonify()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()



def connect_db():
    return sqlite3.connect(app.config['DATABASE'])



if __name__ == "__main__":
    app.debug = False
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
