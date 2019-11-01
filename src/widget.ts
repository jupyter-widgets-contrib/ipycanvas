// Copyright (c) Martin Renou
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers, Dict, ViewList, unpack_models
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';

import {
  getArg
} from './utils';


function getContext(canvas: HTMLCanvasElement) {
  const context = canvas.getContext("2d");
  if (context === null) {
    throw 'Could not create 2d context.';
  }
  return context;
}


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
    this.ctx = getContext(this.canvas);

    this.resizeCanvas();

    this.on('change:size', this.resizeCanvas.bind(this));
    this.on('msg:custom', this.onCommand.bind(this));

    this.send({ event: 'client_ready' }, {});
  }

  private async onCommand(command: any, buffers: any) {
    await this.processCommand(command, buffers);

    this.forEachView((view: CanvasView) => {
      view.updateCanvas();
    });
  }

  private async processCommand(command: any, buffers: any) {
    if (command instanceof Array) {
      let remainingBuffers = buffers;

      for (const subcommand of command) {
        let subbuffers = [];
        if (subcommand.n_buffers) {
          subbuffers = remainingBuffers.slice(0, subcommand.n_buffers);
          remainingBuffers = remainingBuffers.slice(subcommand.n_buffers)
        }
        await this.processCommand(subcommand, subbuffers);
      }
      return;
    }

    switch (command.name) {
      case 'fillRects':
        this.drawRects(command.args, buffers, 'fillRect');
        break;
      case 'strokeRects':
        this.drawRects(command.args, buffers, 'strokeRect');
        break;
      case 'fillArc':
        this.fillArc(command.args, buffers);
        break;
      case 'strokeArc':
        this.strokeArc(command.args, buffers);
        break;
      case 'fillArcs':
        this.drawArcs(command.args, buffers, 'fill');
        break;
      case 'strokeArcs':
        this.drawArcs(command.args, buffers, 'stroke');
        break;
      case 'drawImage':
        await this.drawImage(command.args, buffers);
        break;
      case 'putImageData':
        this.putImageData(command.args, buffers);
        break;
      case 'set':
        this.setAttr(command.attr, command.value);
        break;
      case 'clear':
        this.clearCanvas();
        break;
      default:
        this.executeCommand(command.name, command.args);
        break;
    }
  }

  private drawRects(args: any[], buffers: any, commandName: string) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const width = getArg(args[2], buffers);
    const height = getArg(args[3], buffers);

    const numberRects = Math.min(x.length, y.length, width.length, height.length);

    for (let idx = 0; idx < numberRects; ++idx) {
      this.executeCommand(commandName, [x.getItem(idx), y.getItem(idx), width.getItem(idx), height.getItem(idx)]);
    }
  }

  private fillArc(args: any[], buffers: any) {
    this.ctx.save();

    this.ctx.beginPath();
    this.executeCommand('arc', args);
    this.ctx.closePath();

    this.ctx.fill();
    this.ctx.restore();
  }

  private strokeArc(args: any[], buffers: any) {
    this.ctx.save();

    this.ctx.beginPath();
    this.executeCommand('arc', args);
    this.ctx.closePath();

    this.ctx.stroke();
    this.ctx.restore();
  }

  private drawArcs(args: any[], buffers: any, commandName: string) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const radius = getArg(args[2], buffers);
    const startAngle = getArg(args[3], buffers);
    const endAngle = getArg(args[4], buffers);
    const anticlockwise = getArg(args[5], buffers);

    const numberArcs = Math.min(
      x.length, y.length, radius.length,
      startAngle.length, endAngle.length
    );

    this.ctx.save();

    for (let idx = 0; idx < numberArcs; ++idx) {
      this.ctx.beginPath();
      this.ctx.arc(
        x.getItem(idx), y.getItem(idx), radius.getItem(idx),
        startAngle.getItem(idx), endAngle.getItem(idx),
        anticlockwise.getItem(idx)
      );
      this.ctx.closePath();

      this.executeCommand(commandName);
    }

    this.ctx.restore();
  }

  private async drawImage(args: any[], buffers: any) {
    const [serializedImage, x, y, width, height] = args;

    const image = await unpack_models(serializedImage, this.widget_manager);

    if (image instanceof CanvasModel) {
      this._drawImage(image.canvas, x, y, width, height);
      return;
    }

    if (image.get('_model_name') == 'ImageModel') {
      // Create the image manually instead of creating an ImageView
      let url: string;
      const format = image.get('format');
      const value = image.get('value');
      if (format !== 'url') {
          const blob = new Blob([value], {type: `image/${format}`});
          url = URL.createObjectURL(blob);
      } else {
          url = (new TextDecoder('utf-8')).decode(value.buffer);
      }

      const img = new Image();
      return new Promise((resolve) => {
        img.onload = () => {
          this._drawImage(img, x, y, width, height);
          resolve();
        };
        img.src = url;
      });
    }
  }

  private _drawImage(image: HTMLCanvasElement | HTMLImageElement,
                     x: number, y: number,
                     width: number | undefined, height: number | undefined) {
    if (width === undefined || height === undefined) {
      this.ctx.drawImage(image, x, y);
    } else {
      this.ctx.drawImage(image, x, y, width, height);
    }
  }

  private putImageData(args: any[], buffers: any) {
    const [bufferMetadata, dx, dy] = args;

    const width = bufferMetadata.shape[1];
    const height = bufferMetadata.shape[0];

    const data = new Uint8ClampedArray(buffers[0].buffer);
    const imageData = new ImageData(data, width, height);

    // Draw on a temporary off-screen canvas. This is a workaround for `putImageData` to support transparency.
    const offscreenCanvas = document.createElement('canvas');
    offscreenCanvas.width = width;
    offscreenCanvas.height = height;
    getContext(offscreenCanvas).putImageData(imageData, 0, 0);

    this.ctx.drawImage(offscreenCanvas, dx, dy);
  }

  private setAttr(attr: string, value: any) {
    (this.ctx as any)[attr] = value;
  }

  private clearCanvas() {
    this.forEachView((view: CanvasView) => {
      view.clear();
    });
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  private executeCommand(name: string, args: any[] = []) {
    (this.ctx as any)[name](...args);
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
  ctx: CanvasRenderingContext2D;

  views: Dict<Promise<CanvasView>>;
}


export
class CanvasView extends DOMWidgetView {
  render() {
    this.canvas = document.createElement('canvas');

    this.el.appendChild(this.canvas);
    this.ctx = getContext(this.canvas);

    this.resizeCanvas();
    this.model.on('change:size', this.resizeCanvas.bind(this));

    this.canvas.addEventListener('mousemove', { handleEvent: this.onMouseMove.bind(this) });
    this.canvas.addEventListener('mousedown', { handleEvent: this.onMouseDown.bind(this) });
    this.canvas.addEventListener('mouseup', { handleEvent: this.onMouseUp.bind(this) });
    this.canvas.addEventListener('mouseout', { handleEvent: this.onMouseOut.bind(this) });

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

  private onMouseDown(event: MouseEvent) {
    this.model.send({ event: 'click', ...this.getMouseCoordinate(event) }, {});
    this.model.send({ event: 'mouse_down', ...this.getMouseCoordinate(event) }, {});
  }

  private onMouseMove(event: MouseEvent) {
    this.model.send({ event: 'mouse_move', ...this.getMouseCoordinate(event) }, {});
  }

  private onMouseUp(event: MouseEvent) {
    this.model.send({ event: 'mouse_up', ...this.getMouseCoordinate(event) }, {});
  }

  private onMouseOut(event: MouseEvent) {
    this.model.send({ event: 'mouse_out', ...this.getMouseCoordinate(event) }, {});
  }

  private getMouseCoordinate(event: MouseEvent) {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    return { x, y };
  }

  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;

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
