from ipywidgets import DOMWidget
from traitlets import Int
from ._frontend import module_name, module_version
from traitlets import Unicode


class MyCanvas(DOMWidget):
    """A simple canvas widget with configurable width and height."""

    _model_name = Unicode('MyCanvasModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _view_name = Unicode('MyCanvasView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    width = Int(300).tag(sync=True)
    height = Int(150).tag(sync=True)
