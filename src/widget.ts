// Copyright (c) Martin Renou
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers, Dict
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';

import '../css/ipycanvas.css'


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
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
  }

  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');

    this.resizeCanvas();

    this.on('change:size', this.resizeCanvas.bind(this));
    this.on('msg:custom', this.onCommand.bind(this));
  }

  private onCommand(command: any) {
    this.processCommand(command);

    this.forEachView((view: CanvasView) => {
      view.updateCanvas();
    });
  }

  private processCommand(command: any) {
    if (command instanceof Array) {
      for (const subcommand of command) {
        this.processCommand(subcommand);
      }
      return;
    }

    if (command.name == 'set') {
      this.ctx[command.attr] = command.value;
      return;
    }

    if (command.name == 'clear') {
      this.forEachView((view: CanvasView) => {
        view.clear();
      });
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

      return;
    }

    this.ctx[command.name](...command.args);
  }

  private forEachView(callback: (view: CanvasView) => void) {
    for (const view_id in this.views) {
      this.views[view_id].then((view: CanvasView) => {
        callback(view);
      });
    }
  }

  private resizeCanvas() {
    const size = this.get('size');

    this.canvas.setAttribute('width', size[0]);
    this.canvas.setAttribute('height', size[1]);
  }

  static model_name = 'CanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'CanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;

  canvas: HTMLCanvasElement;
  ctx: any;
  views: Dict<Promise<CanvasView>>;
}


export
class CanvasView extends DOMWidgetView {
  render() {
    this.canvas = document.createElement('canvas');

    this.el.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');

    this.resizeCanvas();
    this.model.on('change:size', this.resizeCanvas.bind(this));

    this.updateCanvas();
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  updateCanvas() {
    this.ctx.drawImage(this.model.canvas, 0, 0);
  }

  private resizeCanvas() {
    const size = this.model.get('size');

    this.canvas.setAttribute('width', size[0]);
    this.canvas.setAttribute('height', size[1]);
  }

  canvas: HTMLCanvasElement;
  ctx: any;

  model: CanvasModel;
}
