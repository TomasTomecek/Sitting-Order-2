function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');        
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var map;
var vector_layer;

//create place frmo name, lon, lat
function create_place(name, lon, lat) {
    var point = new OpenLayers.Geometry.Point(lon, lat);
    var pointFeature = new OpenLayers.Feature.Vector(point);
    pointFeature.attributes = {
        name: name,
        team: "Finance",
        color: 'red',
    }; 
    return pointFeature;
}

// initiate creation of new seat
function init_seat(lonlat) {
    popup = new OpenLayers.Popup("asd",
                       new OpenLayers.LonLat(lonlat.lon, lonlat.lat),
                       new OpenLayers.Size(350,150),
                       "<input type=\"text\" name=\"place_id\" value=\"Enter place id\" class=\"new_place\"/ >",
                       true);

    map.addPopup(popup);

    $(".new_place").click(function(){
        $(this).val("");
    });
    $(".new_place").keyup(function(event){
        if (event.which == 13) {
            var floor_id = $("#floor-select select").val();
            $.post(
                "/ajax/",
                { "lon": lonlat.lon, "lat": lonlat.lat, "id": $(this).val(), "floor_id": floor_id },
                function(data) {
                    if (data["status"] == "ok") {
                        pointFeature = create_place(data['name'], lonlat.lon, lonlat.lat)
                        vector_layer.addFeatures([pointFeature]);
                    }
                }
            );
            popup.destroy();
        }
    });    
}

function place_seat(name, lon, lat) {
    pointFeature = create_place(name, lon, lat)
    vector_layer.addFeatures([pointFeature]);
}

function load_floor(image_path){
   var graphic = new OpenLayers.Layer.Image(
        'Sunset',
        image_path,
        new OpenLayers.Bounds(-500/2, -700/2, 500/2, 700/2),
        new OpenLayers.Size(500, 700),
        {numZoomLevels: 2}
    );

    vector_layer = new OpenLayers.Layer.Vector("vector", {
        styleMap: new OpenLayers.StyleMap({'default': {
            strokeColor: "#000000",
            strokeOpacity: 1,
            strokeWidth: 3,
            fillColor: "#DDD",
            fillOpacity: 1,
            pointRadius: 8,
            pointerEvents: "visiblePainted",
            label : "${name}\n\n${team}",

            fontColor: "${color}",
            fontSize: "14px",
            fontFamily: "Courier New, monospace",
            fontWeight: "bold",
            labelYOffset: "30",
            labelOutlineColor: "white",
            labelOutlineWidth: 3
        }}),
        eventListeners: {
            'featureselected':function(evt){
                var feature = evt.feature;
                var popup = new OpenLayers.Popup.FramedCloud("popup",
                    OpenLayers.LonLat.fromString(feature.geometry.toShortString()),
                    null,
                    "<div style='font-size:1.2em; background-color: white;'>Feature: " + feature.id +"<br>Foo: " + feature.attributes.foo+"</div>",
                    null,
                    true
                );
                feature.popup = popup;
                map.addPopup(popup);
            },
            'featureunselected':function(evt){
                var feature = evt.feature;
                map.removePopup(feature.popup);
                feature.popup.destroy();
                feature.popup = null;
            }
        }
    });

    var selector = new OpenLayers.Control.SelectFeature(vector_layer, {
        //hover:true,
        autoActivate:true,
        clickout:true
    });

    map.addLayers([graphic, vector_layer]);
    map.addControl(selector);
    //map.addControl(new OpenLayers.Control.MousePosition());
    map.zoomToMaxExtent();

    map.events.register("click", map, function(e) {
        // what control is selected? "create" or "select"
        if ($("#controlsForm input[type='radio']:checked").val() == "select") {
            return;
        }
        var position = this.events.getMousePosition(e);
        var lonlat = map.getLonLatFromPixel(position);
        init_seat(lonlat)
    });
}

function setup_env(){
    // http://docs.openlayers.org/library/deploying.html
    OpenLayers.ImgPath = "/static/images/ol/"
    map = new OpenLayers.Map('map', { theme: null });

    //create_place(vectorLayer, new OpenLayers.LonLat(0.0, 0.0))

    /*
     * Controls
     *
     */
/*
    selectControl = new OpenLayers.Control.SelectFeature(
        vectorLayer,
        {onSelect: onFeatureSelect, onUnselect: onFeatureUnselect});
    drawControls = {
        polygon: new OpenLayers.Control.DrawFeature(vectorLayer,
                    OpenLayers.Handler.Polygon),
        select: selectControl
    };

    for(var key in drawControls) {
        map.addControl(drawControls[key]);
    }

    /* MARKERS
    var markerslayer = new OpenLayers.Layer.Markers("Markers");
    map.addLayer(markerslayer);

    map.events.register("click", map, function(e) {
        var position = this.events.getMousePosition(e);
        var icon = new OpenLayers.Icon('http://maps.google.com/mapfiles/ms/icons/red-pushpin.png');
        var lonlat = map.getLonLatFromPixel(position);
        alert(lonlat);
        markerslayer.addMarker(new OpenLayers.Marker(lonlat, icon));
    });
    */
}

function assign_handlers() {
    $("#floor-select").change(function() {
        var select = $(this).find("select");
        var value = select.val();
        if (value != "") {
            $.get(
                '/ajax/floor/' + value + "/",
                function(data) {
                    load_floor(data['image_path']);
                }        
            );
            $.get(
                '/ajax/floor/' + value + '/all/',
                function(data) {
                    $.each(data, function(index, item){
                        place_seat(item["name"], item["lon"], item["lat"]);
                    });
                }        
            );            
        } else {
            // unload map, or?
        }     
    });
}

$(document).ready(function() {
    setup_env();
    assign_handlers();
});