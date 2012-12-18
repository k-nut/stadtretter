var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];

all_the_markers = [];

function initmap() {
        // set up the map
        map = new L.Map('map');

        // create the tile layer with correct attribution
        var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
        var osmAttrib='Map data © OpenStreetMap contributors';
        var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 18, attribution: osmAttrib});		

        // start the map in South-East England
        map.setView(new L.LatLng(52.52, 13.41),13);
        map.addLayer(osm);
}

var add_icon = new L.Icon({iconUrl: '/static/img/new_marker.png',
        iconSize: [25, 41],
    iconAnchor: [13, 41],
    popupAnchor: [-3, -76],
    shadowUrl: 'http://cdn.leafletjs.com/leaflet-0.4.4/images/marker-shadow.png',
    shadowSize: [68, 95],
    shadowAnchor: [22, 94]
});

function new_marker(lat, lon, title, name, picture){
        this_marker = L.marker([lat, lon], clickable=true);
        this_marker.bindPopup("<img class='pull-right' width='40px' src='" + picture + "' /> <strong>" + title + "</strong> <p>" + name +"</p>" );
        this_marker.addTo(map);
}

is_adding_marker = false;
var t;

function add_new_marker(){
        if (!is_adding_marker){
                is_adding_marker = true;
                $("#action-explanation").modal();
                this_marker = L.marker(map.getCenter(), {"icon": add_icon, "draggable":true});
                this_marker.on('dragend', function(){
                        $("#lat-input").val(this.getLatLng().lat);
                        $("#lng-input").val(this.getLatLng().lng);
                        clearTimeout(t);
                        t = setTimeout(function(){$("#action-dialogue").modal();}, 2000);
                });
                this_marker.addTo(map);
                $(".popup").toggle();
        }
        setTimeout(function(){
                $("#lat-input").val(this_marker.getLatLng().lat);
                $("#lng-input").val(this_marker.getLatLng().lng);
        },500
        );
}
function closepopup(){
        $(".popup").toggle();
        map.removeLayer(new_marker);
        is_adding_marker = false;
}

function zoom(query){
        $.getJSON("/getCoordinates/" + query, function(data){
                if (data.lat){
                        map.panTo([data.lat, data.lon]);
                }
                else {
                        $("#notfound").fadeIn(750, function(){$("#notfound").fadeOut(2000);}); 
                }
        });
}

function getMarkers(north, east, south, west){
        $.getJSON("/get-markers/" + north +"/" + east + "/" + south + "/" + west, function(data){
                var result = data.marker;
                for (i=0; i<result.length; i++){
                        now = result[i];
                        if (all_the_markers.indexOf(now.id) == -1){
                                new_marker(now.lat, now.lon, now.title, now.name, now.picture);
                                all_the_markers.push(now.id);
                        }
                }
        });
}

function doit(){
        var box = map.getBounds();
        getMarkers(box._southWest.lat, box._northEast.lat, box._southWest.lng, box._northEast.lng);
}


function get_user_position(){
        if (navigator.geolocation){
                navigator.geolocation.getCurrentPosition(function(position){
                        coords = [position.coords.latitude, position.coords.longitude];
                });
        }
        else {
                coords = false;
        }
        return coords;
}
