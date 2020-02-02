#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Martin Renou.
# Distributed under the terms of the Modified BSD License.

from traitlets import Any, CFloat, Dict, Unicode, validate

from ipywidgets import Widget

from ._frontend import module_name, module_version

from .py2js import py2js


class Animation(Widget):
    """Custom Canvas animation."""

    _model_name = Unicode('AnimationModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('AnimationView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # TODO: Custom Functor trait
    #: (functor) The draw function that will be called for every animation frame. This function should
    #: take the ``Canvas`` as first argument, the elapsed time (in ms) since the beginning of the animation
    #: as second argument, and custom data as third argument.
    draw = Any(allow_none=False)

    _draw = Unicode().tag(sync=True)

    #: (float) The animation duration (in ms), if ``0`` the animation will run infinitely.
    duration = CFloat(0).tag(sync=True)

    #: (dict) Custom data to be passed to the draw function.
    data = Dict().tag(sync=True)

    @validate('draw')
    def _validate_draw(self, proposal):
        self._draw = py2js(proposal['value'])

        return proposal['value']
