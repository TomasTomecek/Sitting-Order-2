# -*- coding: utf-8 -*-

from django import forms

from sit.models import Floor


class FloorChoiceForm(forms.Form):
    floor = forms.ModelChoiceField(queryset=Floor.objects.all(),
                                   empty_label="Select floor to display")