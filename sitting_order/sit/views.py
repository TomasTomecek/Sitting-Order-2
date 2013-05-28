# -*- coding: utf-8 -*-

import json

from django.views.generic import TemplateView
from django import http
from django.shortcuts import get_object_or_404
from sit.models import *
from sit.forms import FloorChoiceForm

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self):
        context = {}
        context['floors_form'] = FloorChoiceForm()
        return context

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json; charset=utf-8',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


class AjaxView(JSONResponseMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        post = request.POST
        p = Place(lon=post['lon'], lat=post['lat'],
                  floor=get_object_or_404(Floor, pk=post['floor_id']))
        s = get_object_or_404(Seat, number=post['id'])
        p.seat = s
        p.save()
        return JSONResponseMixin.render_to_response(
            self, {
                'status': 'ok',
                'name': s.user.name
            }
        )

class AjaxFloorView(JSONResponseMixin, TemplateView):
    def get(self, request, floor_id, *args, **kwargs):
        floor = get_object_or_404(Floor, pk=floor_id)
        response = {}
        response['image_path'] = floor.image
        return JSONResponseMixin.render_to_response(
            self, response
        )


class AjaxAllView(JSONResponseMixin, TemplateView):
    def get(self, request, floor_id, *args, **kwargs):
        response = []
        places = Place.objects.filter(floor__id=floor_id)
        for p in places:
            response.append({
                'name': p.seat.user.name,
                'lon': p.lon,
                'lat': p.lat
            })
        return JSONResponseMixin.render_to_response(
            self, response
        )