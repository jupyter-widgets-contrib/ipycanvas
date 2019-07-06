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
      size: [],
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
  }

  model_events() {
    this.model.on('msg:custom', (event) => {
      this.ctx.fillStyle = this.model.get('fill_style');
      this.ctx.strokeStyle = this.model.get('stroke_style');

      this.ctx[event.msg](...event.args);
    });

    this.model.on('change;size', () => { this.resize_canvas(); });
  }

  resize_canvas() {
    const size = this.model.get('size');

    this.canvas.setAttribute('width', size[0]);
    this.canvas.setAttribute('height', size[1]);
  }

  canvas: any;
  ctx: any;
}
