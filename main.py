from flask import Flask, request, g, redirect, url_for, \
        abort, render_template, jsonify, json
from flask_sqlalchemy import SQLAlchemy
import urllib, urllib2
import datetime
from werkzeug import secure_filename
import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('stadtretter.cfg', silent=False)
if os.environ.get("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    db = SQLAlchemy(app)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
    db = SQLAlchemy(app)

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pubdate = db.Column(db.Date, index=True)
    name = db.Column(db.String(80))
    title = db.Column(db.String(300))
    picture = db.Column(db.String(300))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    def __init__(self, name, title, picture, lat, lon):
        self.name = name
        self.title = title
        self.picture = picture
        self.lat = lat
        self.lon = lon
        self.pubdate = datetime.date.today()

    def __repr__(self):
        return '<User %r>' % self.name


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    ''' Render the main page '''
    return render_template("index.html")

@app.route("/get-markers/<south>/<north>/<west>/<east>")
def markers(south, north, west, east):
    ''' Get all the markers within a bounding box '''
    result = Action.query.filter(
            Action.lat.between(float(south),float(north)),
            Action.lon.between(float(west), float(east))
            ).all()
    return jsonify(marker=[dict(
        id=action.id,
        name=action.name,
        title=action.title,
        picture="/static/user-images/"+action.picture if action.picture else "",
        lat=action.lat,
        lon=action.lon
        ) for action in result])

@app.route('/add', methods=['POST'])
def add_entry():
    ''' Add a new marker to the db '''
    userfile = request.files["picture"]
    if userfile and allowed_file(userfile.filename):
        filename = secure_filename(userfile.filename)
        userfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = ""
    new_action = Action(
            name = request.form.get("name"),
            title = request.form.get("title"),
            picture = filename,
            lat = request.form.get("lat"),
            lon = request.form.get("lon")
            )
    db.session.add(new_action)
    db.session.commit()
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

if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
