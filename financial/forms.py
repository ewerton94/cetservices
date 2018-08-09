# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from .models import Entrance


class EntranceForm(forms.ModelForm):
    class Meta:
        model = Entrance
        fields = ('value', 'description')

    def __init__(self, *args, **kwargs):
        super(EntranceForm, self).__init__(*args, **kwargs)

        # you can iterate all fields here
        for fname, f in self.fields.items():
            f.widget.attrs['class'] = 'form-control'