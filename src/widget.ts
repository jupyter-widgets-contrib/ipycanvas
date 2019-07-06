// Copyright (c) Martin Renou
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';

import './canvas.css';


export
class CanvasModel extends DOMWidgetModel {
  defaults() {
    return {...super.defaults(),
      _model_name: CanvasModel.model_name,
      _model_module: CanvasModel.model_module,
      _model_module_version: CanvasModel.model_module_version,
      _view_name: CanvasModel.view_name,
      _view_module: CanvasModel.view_module,
      _view_module_version: CanvasModel.view_module_version,
      fill_style: 'black',
      stroke_style: 'black'
    };
  }

  static serializers: ISerializers = {
      ...DOMWidgetModel.serializers,
      // Add any extra serializers here
    }

  static model_name = 'CanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'CanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}


export
class CanvasView extends DOMWidgetView {
  render() {
    this.canvas = document.createElement('canvas');
    this.canvas.classList.add('ipycanvas_canvas');

    this.ctx = this.canvas.getContext('2d');

    this.el.appendChild(this.canvas);
    this.el.classList.add('ipycanvas');

    this.resize_canvas();

    this.model_events();

    window.addEventListener('resize', () => { this.resize_canvas(); });
  }

  model_events() {
    this.model.on('msg:custom', (event) => {
      this.ctx.fillStyle = this.model.get('fill_style');
      this.ctx.strokeStyle = this.model.get('stroke_style');

      this.ctx[event.msg](...event.args);
    });
  }

  processPhosphorMessage(msg: any) {
    super.processPhosphorMessage(msg);

    switch (msg.type) {
    case 'resize':
      this.resize_canvas();
      break;
    }
  }

  resize_canvas() {
    // TODO replay all drawings after resize?

    const rect = this.el.getBoundingClientRect();
    this.canvas.setAttribute('width', rect.width);
    this.canvas.setAttribute('height', rect.height);
  }

  canvas: any;
  ctx: any;
}
