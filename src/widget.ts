// Copyright (c) Martin Renou
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers, Dict, ViewList, unpack_models
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
      size: [700, 500],
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


export
class MultiCanvasModel extends DOMWidgetModel {
  defaults() {
    return {...super.defaults(),
      _model_name: MultiCanvasModel.model_name,
      _model_module: MultiCanvasModel.model_module,
      _model_module_version: MultiCanvasModel.model_module_version,
      _view_name: MultiCanvasModel.view_name,
      _view_module: MultiCanvasModel.view_module,
      _view_module_version: MultiCanvasModel.view_module_version,
      _canvases: [],
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    _canvases: { deserialize: (unpack_models as any) },
  }

  static model_name = 'MultiCanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'MultiCanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}


export
class MultiCanvasView extends DOMWidgetView {
  render() {
    this.container = document.createElement('div');
    this.container.style.position = 'relative';

    this.el.appendChild(this.container);

    this.canvas_views = new ViewList<CanvasView>(this.createCanvasView, this.removeCanvasView, this);
    this.updateCanvasViews();

    this.model.on('change:_canvases', this.updateCanvasViews.bind(this));
  }

  private updateCanvasViews() {
    this.canvas_views.update(this.model.get('_canvases'));
  }

  private createCanvasView(canvasModel: CanvasModel, index: number) {
    // The following ts-ignore is needed due to ipywidgets's implementation
    // @ts-ignore
    return this.create_child_view(canvasModel).then((canvasView: CanvasView) => {
      canvasView.el.style.zIndex = index;
      canvasView.el.style.position = 'absolute';
      this.container.appendChild(canvasView.el);

      return canvasView;
    });
  }

  private removeCanvasView(canvasView: CanvasView) {
    this.container.removeChild(canvasView.el);
  }

  private container: HTMLDivElement;
  private canvas_views: ViewList<CanvasView>;
}
