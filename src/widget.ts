// Copyright (c) Martin Renou
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';


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

    this.commandsCache = [];

    this.on('msg:custom', (command) => {
      if (!(command instanceof Array) && command.name == 'clear') {
        this.commandsCache = [];
        return;
      }

      this.commandsCache.push(command);
    });
  }

  static model_name = 'CanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'CanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;

  commandsCache: Array<any>;
}


export
class CanvasView extends DOMWidgetView {
  render() {
    this.canvas = document.createElement('canvas');
    this.canvas.width = '100%';
    this.canvas.height = '100%';

    this.el.appendChild(this.canvas);
    this.el.height = '500px';
    this.el.overflow = 'hidden';
    this.el.flex = '1 1 auto';

    this.ctx = this.canvas.getContext('2d');

    this.resize_canvas();

    this.firstDraw();

    this.modelEvents();
  }

  firstDraw() {
    // Replay all the commands that were received until this view was created
    for (const command of this.model.commandsCache) {
      this._processCommand(command);
    }
  }

  modelEvents() {
    this.model.on('msg:custom', this._processCommand.bind(this));
  }

  private _processCommand (command: any) {
    if (command instanceof Array) {
      for (const subcommand of command) {
        this._processCommand(subcommand);
      }
      return;
    }

    if (command.name == 'clear') {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      return;
    }

    if (command.name == 'set') {
      this.ctx[command.attr] = command.value;
      return;
    }

    this.ctx[command.name](...command.args);
  }

  resize_canvas() {
    const size = this.model.get('size');

    this.canvas.setAttribute('width', size[0]);
    this.canvas.setAttribute('height', size[1]);
  }

  canvas: any;
  ctx: any;
  model: CanvasModel;
}
