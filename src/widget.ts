// Copyright (c) Martin Renou
// Distributed under the terms of the Modified BSD License.

import { Buffer } from 'buffer';

import {
  DOMWidgetModel,
  DOMWidgetView,
  WidgetModel,
  ISerializers,
  Dict,
  unpack_models
} from '@jupyter-widgets/base';

import { RoughCanvas } from 'roughjs/bin/canvas';

import { MODULE_NAME, MODULE_VERSION } from './version';

import { getArg, toBytes, fromBytes, getTypedArray } from './utils';

function getContext(canvas: HTMLCanvasElement) {
  const context = canvas.getContext('2d');
  if (context === null) {
    throw 'Could not create 2d context.';
  }
  return context;
}

function serializeImageData(array: Uint8ClampedArray) {
  return new DataView(array.buffer.slice(0));
}

function deserializeImageData(dataview: DataView | null) {
  if (dataview === null) {
    return null;
  }

  return new Uint8ClampedArray(dataview.buffer);
}

async function createImageFromWidget(
  image: DOMWidgetModel
): Promise<HTMLImageElement> {
  // Create the image manually instead of creating an ImageView
  let url: string;
  const format = image.get('format');
  const value = image.get('value');
  if (format !== 'url') {
    const blob = new Blob([value], { type: `image/${format}` });
    url = URL.createObjectURL(blob);
  } else {
    url = new TextDecoder('utf-8').decode(value.buffer);
  }

  const img = new Image();
  return new Promise(resolve => {
    img.onload = () => {
      resolve(img);
    };
    img.src = url;
  });
}

const COMMANDS = [
  'fillRect',
  'strokeRect',
  'fillRects',
  'strokeRects',
  'clearRect',
  'fillArc',
  'fillCircle',
  'strokeArc',
  'strokeCircle',
  'fillArcs',
  'strokeArcs',
  'fillCircles',
  'strokeCircles',
  'strokeLine',
  'beginPath',
  'closePath',
  'stroke',
  'fillPath',
  'fill',
  'moveTo',
  'lineTo',
  'rect',
  'arc',
  'ellipse',
  'arcTo',
  'quadraticCurveTo',
  'bezierCurveTo',
  'fillText',
  'strokeText',
  'setLineDash',
  'drawImage',
  'putImageData',
  'clip',
  'save',
  'restore',
  'translate',
  'rotate',
  'scale',
  'transform',
  'setTransform',
  'resetTransform',
  'set',
  'clear',
  'sleep',
  'fillPolygon',
  'strokePolygon',
  'strokeLines',
  'fillPolygons',
  'strokePolygons',
  'strokeLineSegments',
  'fillStyledRects',
  'strokeStyledRects',
  'fillStyledCircles',
  'strokeStyledCircles',
  'fillStyledArcs',
  'strokeStyledArcs',
  'fillStyledPolygons',
  'strokeStyledPolygons',
  'strokeStyledLineSegments',
  'switchCanvas'
];

export class CanvasManagerModel extends WidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: CanvasManagerModel.model_name,
      _model_module: CanvasManagerModel.model_module,
      _model_module_version: CanvasManagerModel.model_module_version
    };
  }

  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    this.on('msg:custom', this.onCommand.bind(this));
  }

  private async onCommand(command: any, buffers: any) {
    // Retrieve the commands buffer as an object (list of commands)
    const commands = JSON.parse(
      Buffer.from(getTypedArray(buffers[0], command)).toString('utf-8')
    );

    this.canvasesToUpdate =
      this.currentCanvas !== undefined ? [this.currentCanvas] : [];

    await this.processCommand(commands, buffers.slice(1, buffers.length));

    for (const canvas of this.canvasesToUpdate) {
      canvas.syncViews();
    }
  }

  private async processCommand(command: any, buffers: any) {
    // If it's a list of commands
    if (command instanceof Array && command[0] instanceof Array) {
      let remainingBuffers = buffers;

      for (const subcommand of command) {
        let subbuffers = [];
        const nBuffers: Number = subcommand[2];
        if (nBuffers) {
          subbuffers = remainingBuffers.slice(0, nBuffers);
          remainingBuffers = remainingBuffers.slice(nBuffers);
        }
        await this.processCommand(subcommand, subbuffers);
      }
      return;
    }

    const name: string = COMMANDS[command[0]];
    const args: any[] = command[1];
    switch (name) {
      case 'switchCanvas':
        await this.switchCanvas(args[0]);
        this.canvasesToUpdate.push(this.currentCanvas);
        break;
      case 'sleep':
        await this.currentCanvas.sleep(args[0]);
        break;
      case 'fillRect':
        this.currentCanvas.fillRect(args[0], args[1], args[2], args[3]);
        break;
      case 'strokeRect':
        this.currentCanvas.strokeRect(args[0], args[1], args[2], args[3]);
        break;
      case 'fillRects':
        this.currentCanvas.drawRects(
          args,
          buffers,
          this.currentCanvas.fillRect.bind(this.currentCanvas)
        );
        break;
      case 'strokeRects':
        this.currentCanvas.drawRects(
          args,
          buffers,
          this.currentCanvas.strokeRect.bind(this.currentCanvas)
        );
        break;
      case 'fillArc':
        this.currentCanvas.fillArc(
          args[0],
          args[1],
          args[2],
          args[3],
          args[4],
          args[5]
        );
        break;
      case 'strokeArc':
        this.currentCanvas.strokeArc(
          args[0],
          args[1],
          args[2],
          args[3],
          args[4],
          args[5]
        );
        break;
      case 'fillArcs':
        this.currentCanvas.drawArcs(
          args,
          buffers,
          this.currentCanvas.fillArc.bind(this.currentCanvas)
        );
        break;
      case 'strokeArcs':
        this.currentCanvas.drawArcs(
          args,
          buffers,
          this.currentCanvas.strokeArc.bind(this.currentCanvas)
        );
        break;
      case 'fillCircle':
        this.currentCanvas.fillCircle(args[0], args[1], args[2]);
        break;
      case 'strokeCircle':
        this.currentCanvas.strokeCircle(args[0], args[1], args[2]);
        break;
      case 'fillCircles':
        this.currentCanvas.drawCircles(
          args,
          buffers,
          this.currentCanvas.fillCircle.bind(this.currentCanvas)
        );
        break;
      case 'strokeCircles':
        this.currentCanvas.drawCircles(
          args,
          buffers,
          this.currentCanvas.strokeCircle.bind(this.currentCanvas)
        );
        break;
      case 'strokeLine':
        this.currentCanvas.strokeLine(args, buffers);
        break;
      case 'strokeLines':
        this.currentCanvas.strokeLines(args, buffers);
        break;
      case 'fillPolygon':
        this.currentCanvas.fillPolygon(args, buffers);
        break;
      case 'strokePolygon':
        this.currentCanvas.strokePolygon(args, buffers);
        break;
      case 'fillPath':
        await this.currentCanvas.fillPath(args, buffers);
        break;
      case 'drawImage':
        await this.currentCanvas.drawImage(args, buffers);
        break;
      case 'putImageData':
        this.currentCanvas.putImageData(args, buffers);
        break;
      case 'set':
        await this.currentCanvas.setAttr(args[0], args[1]);
        break;
      case 'clear':
        this.currentCanvas.clearCanvas();
        break;
      case 'fillPolygons':
        this.currentCanvas.drawPolygonOrLineSegments(args, buffers, true, true);
        break;
      case 'strokePolygons':
        this.currentCanvas.drawPolygonOrLineSegments(
          args,
          buffers,
          false,
          true
        );
        break;
      case 'strokeLineSegments':
        this.currentCanvas.drawPolygonOrLineSegments(
          args,
          buffers,
          false,
          false
        );
        break;
      case 'fillStyledRects':
        this.currentCanvas.drawStyledRects(args, buffers, true);
        break;
      case 'strokeStyledRects':
        this.currentCanvas.drawStyledRects(args, buffers, false);
        break;
      case 'fillStyledCircles':
        this.currentCanvas.drawStyledCircles(args, buffers, true);
        break;
      case 'strokeStyledCircles':
        this.currentCanvas.drawStyledCircles(args, buffers, false);
        break;
      case 'fillStyledArcs':
        this.currentCanvas.drawStyledArcs(args, buffers, true);
        break;
      case 'strokeStyledArcs':
        this.currentCanvas.drawStyledArcs(args, buffers, false);
        break;
      case 'fillStyledPolygons':
        this.currentCanvas.drawStyledPolygonOrLineSegments(
          args,
          buffers,
          true,
          true
        );
        break;
      case 'strokeStyledPolygons':
        this.currentCanvas.drawStyledPolygonOrLineSegments(
          args,
          buffers,
          false,
          true
        );
        break;
      case 'strokeStyledLineSegments':
        this.currentCanvas.drawStyledPolygonOrLineSegments(
          args,
          buffers,
          false,
          false
        );
        break;
      default:
        this.currentCanvas.executeCommand(name, args);
        break;
    }
  }

  private async switchCanvas(serializedCanvas: any) {
    this.currentCanvas = await unpack_models(
      serializedCanvas,
      this.widget_manager
    );
  }

  private currentCanvas: CanvasModel;
  private canvasesToUpdate: CanvasModel[] = [];

  static model_name = 'CanvasManagerModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
}

export class Path2DModel extends WidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: Path2DModel.model_name,
      _model_module: Path2DModel.model_module,
      _model_module_version: Path2DModel.model_module_version,
      value: ''
    };
  }

  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    this.value = new Path2D(this.get('value'));
  }

  value: Path2D;

  static model_name = 'Path2DModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
}

export class PatternModel extends WidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: PatternModel.model_name,
      _model_module: PatternModel.model_module,
      _model_module_version: PatternModel.model_module_version,
      image: '',
      repetition: 'repeat'
    };
  }

  async initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    const image = this.get('image');
    let patternSource: HTMLCanvasElement | HTMLImageElement | undefined =
      undefined;

    if (image instanceof CanvasModel || image instanceof MultiCanvasModel) {
      patternSource = image.canvas;
    }

    if (image.get('_model_name') == 'ImageModel') {
      const img = await createImageFromWidget(image);
      patternSource = img;
    }

    if (patternSource == undefined) {
      throw 'Could not understand the souce for the pattern';
    }

    const pattern = PatternModel.ctx.createPattern(
      patternSource,
      this.get('repetition')
    );

    if (pattern == null) {
      throw 'Could not initialize pattern object';
    }

    this.value = pattern;
  }

  static serializers: ISerializers = {
    ...WidgetModel.serializers,
    image: { deserialize: unpack_models as any }
  };

  value: CanvasPattern;

  static model_name = 'PatternModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;

  // Global context for creating the gradients
  static ctx: CanvasRenderingContext2D = getContext(
    document.createElement('canvas')
  );
}

class GradientModel extends WidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_module: GradientModel.model_module,
      _model_module_version: GradientModel.model_module_version,
      x0: 0,
      y0: 0,
      x1: 0,
      y1: 0,
      color_stops: []
    };
  }

  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    this.createGradient();

    for (const colorStop of this.get('color_stops')) {
      this.value.addColorStop(colorStop[0], colorStop[1]);
    }
  }

  protected createGradient() {
    this.value = GradientModel.ctx.createLinearGradient(
      this.get('x0'),
      this.get('y0'),
      this.get('x1'),
      this.get('y1')
    );
  }

  value: CanvasGradient;

  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;

  // Global context for creating the gradients
  static ctx: CanvasRenderingContext2D = getContext(
    document.createElement('canvas')
  );
}

export class LinearGradientModel extends GradientModel {
  defaults() {
    return { ...super.defaults(), _model_name: LinearGradientModel.model_name };
  }

  static model_name = 'LinearGradientModel';
}

export class RadialGradientModel extends GradientModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: RadialGradientModel.model_name,
      r0: 0,
      r1: 0
    };
  }

  protected createGradient() {
    this.value = GradientModel.ctx.createRadialGradient(
      this.get('x0'),
      this.get('y0'),
      this.get('r0'),
      this.get('x1'),
      this.get('y1'),
      this.get('r1')
    );
  }

  static model_name = 'RadialGradientModel';
}

export class CanvasModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: CanvasModel.model_name,
      _model_module: CanvasModel.model_module,
      _model_module_version: CanvasModel.model_module_version,
      _view_name: CanvasModel.view_name,
      _view_module: CanvasModel.view_module,
      _view_module_version: CanvasModel.view_module_version,
      width: 700,
      height: 500,
      sync_image_data: false,
      image_data: null,
      _send_client_ready_event: true
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    image_data: {
      serialize: serializeImageData,
      deserialize: deserializeImageData
    }
  };

  static ATTRS = [
    'fillStyle',
    'strokeStyle',
    'globalAlpha',
    'font',
    'textAlign',
    'textBaseline',
    'direction',
    'globalCompositeOperation',
    'lineWidth',
    'lineCap',
    'lineJoin',
    'miterLimit',
    'lineDashOffset',
    'shadowOffsetX',
    'shadowOffsetY',
    'shadowBlur',
    'shadowColor',
    'filter'
  ];

  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    this.canvas = document.createElement('canvas');
    this.ctx = getContext(this.canvas);

    this.resizeCanvas();
    this.drawImageData();

    this.on_some_change(['width', 'height'], this.resizeCanvas, this);
    this.on('change:sync_image_data', this.syncImageData.bind(this));
    // this.on('msg:custom', this.onCommand.bind(this));

    if (this.get('_send_client_ready_event')) {
      this.send({ event: 'client_ready' }, {});
    }
  }

  private async drawImageData() {
    if (this.get('image_data') !== null) {
      const img = await fromBytes(this.get('image_data'));

      this.ctx.drawImage(img, 0, 0);

      this.trigger('new-frame');
    }
  }

  async syncViews() {
    this.forEachView((view: CanvasView) => {
      view.updateCanvas();
    });

    this.trigger('new-frame');
    this.syncImageData();
  }

  async sleep(time: number) {
    this.forEachView((view: CanvasView) => {
      view.updateCanvas();
    });

    this.trigger('new-frame');
    this.syncImageData();

    await new Promise(resolve => setTimeout(resolve, time));
  }

  fillRect(x: number, y: number, width: number, height: number) {
    this.ctx.fillRect(x, y, width, height);
  }

  strokeRect(x: number, y: number, width: number, height: number) {
    this.ctx.strokeRect(x, y, width, height);
  }

  drawRects(
    args: any[],
    buffers: any,
    callback: (x: number, y: number, width: number, height: number) => void
  ) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const width = getArg(args[2], buffers);
    const height = getArg(args[3], buffers);

    const numberRects = Math.min(
      x.length,
      y.length,
      width.length,
      height.length
    );

    for (let idx = 0; idx < numberRects; ++idx) {
      callback(
        x.getItem(idx),
        y.getItem(idx),
        width.getItem(idx),
        height.getItem(idx)
      );
    }
  }

  drawStyledRects(args: any[], buffers: any, fill: boolean) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const width = getArg(args[2], buffers);
    const height = getArg(args[3], buffers);
    const colors = getArg(args[4], buffers);
    const alpha = getArg(args[5], buffers);

    const numberRects = Math.min(
      x.length,
      y.length,
      width.length,
      height.length
    );

    this.ctx.save();
    for (let idx = 0; idx < numberRects; ++idx) {
      // get color for this circle
      const ci = 3 * idx;
      const color = `rgba(${colors.getItem(ci)}, ${colors.getItem(
        ci + 1
      )}, ${colors.getItem(ci + 2)}, ${alpha.getItem(idx)})`;
      this.setStyle(color, fill);
      if (fill) {
        this.fillRect(
          x.getItem(idx),
          y.getItem(idx),
          width.getItem(idx),
          height.getItem(idx)
        );
      } else {
        this.strokeRect(
          x.getItem(idx),
          y.getItem(idx),
          width.getItem(idx),
          height.getItem(idx)
        );
      }
    }
    this.ctx.restore();
  }

  fillArc(
    x: number,
    y: number,
    radius: number,
    startAngle: number,
    endAngle: number,
    anticlockwise: boolean
  ) {
    this.ctx.beginPath();

    this.ctx.moveTo(x, y); // Move to center
    this.ctx.lineTo(
      x + radius * Math.cos(startAngle),
      y + radius * Math.sin(startAngle)
    ); // Line to beginning of the arc
    this.ctx.arc(x, y, radius, startAngle, endAngle, anticlockwise);
    this.ctx.lineTo(x, y); // Line to center
    this.ctx.fill();

    this.ctx.closePath();
  }

  strokeArc(
    x: number,
    y: number,
    radius: number,
    startAngle: number,
    endAngle: number,
    anticlockwise: boolean
  ) {
    this.ctx.beginPath();

    this.ctx.arc(x, y, radius, startAngle, endAngle, anticlockwise);
    this.ctx.stroke();

    this.ctx.closePath();
  }

  drawArcs(
    args: any[],
    buffers: any,
    callback: (
      x: number,
      y: number,
      radius: number,
      startAngle: number,
      endAngle: number,
      anticlockwise: boolean
    ) => void
  ) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const radius = getArg(args[2], buffers);
    const startAngle = getArg(args[3], buffers);
    const endAngle = getArg(args[4], buffers);
    const anticlockwise = getArg(args[5], buffers);

    const numberArcs = Math.min(
      x.length,
      y.length,
      radius.length,
      startAngle.length,
      endAngle.length
    );

    for (let idx = 0; idx < numberArcs; ++idx) {
      callback(
        x.getItem(idx),
        y.getItem(idx),
        radius.getItem(idx),
        startAngle.getItem(idx),
        endAngle.getItem(idx),
        anticlockwise.getItem(idx)
      );
    }
  }

  fillCircle(x: number, y: number, radius: number) {
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
    this.ctx.fill();

    this.ctx.closePath();
  }

  strokeCircle(x: number, y: number, radius: number) {
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
    this.ctx.stroke();

    this.ctx.closePath();
  }

  drawCircles(
    args: any[],
    buffers: any,
    callback: (x: number, y: number, radius: number) => void
  ) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const radius = getArg(args[2], buffers);

    const numberCircles = Math.min(x.length, y.length, radius.length);

    for (let idx = 0; idx < numberCircles; ++idx) {
      callback(x.getItem(idx), y.getItem(idx), radius.getItem(idx));
    }
  }

  setStyle(style: any, fill: boolean) {
    if (fill) {
      this.ctx.fillStyle = style;
    } else {
      this.ctx.strokeStyle = style;
    }
  }

  drawStyledCircles(args: any[], buffers: any, fill: boolean) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const radius = getArg(args[2], buffers);
    const colors = getArg(args[3], buffers);
    const alpha = getArg(args[4], buffers);

    const numberCircles = Math.min(x.length, y.length, radius.length);
    this.ctx.save();
    for (let idx = 0; idx < numberCircles; ++idx) {
      // get color for this circle
      const ci = 3 * idx;
      const color = `rgba(${colors.getItem(ci)}, ${colors.getItem(
        ci + 1
      )}, ${colors.getItem(ci + 2)}, ${alpha.getItem(idx)})`;
      this.setStyle(color, fill);
      if (fill) {
        this.fillCircle(x.getItem(idx), y.getItem(idx), radius.getItem(idx));
      } else {
        this.strokeCircle(x.getItem(idx), y.getItem(idx), radius.getItem(idx));
      }
    }
    this.ctx.restore();
  }

  drawStyledArcs(args: any[], buffers: any, fill: boolean) {
    const x = getArg(args[0], buffers);
    const y = getArg(args[1], buffers);
    const radius = getArg(args[2], buffers);
    const startAngle = getArg(args[3], buffers);
    const endAngle = getArg(args[4], buffers);
    const anticlockwise = getArg(args[5], buffers);
    const colors = getArg(args[6], buffers);
    const alpha = getArg(args[7], buffers);

    const numberArcs = Math.min(
      x.length,
      y.length,
      radius.length,
      startAngle.length,
      endAngle.length
    );

    this.ctx.save();
    for (let idx = 0; idx < numberArcs; ++idx) {
      // get color for this circle
      const ci = 3 * idx;
      const color = `rgba(${colors.getItem(ci)}, ${colors.getItem(
        ci + 1
      )}, ${colors.getItem(ci + 2)}, ${alpha.getItem(idx)})`;
      this.setStyle(color, fill);
      if (fill) {
        this.fillArc(
          x.getItem(idx),
          y.getItem(idx),
          radius.getItem(idx),
          startAngle.getItem(idx),
          endAngle.getItem(idx),
          anticlockwise.getItem(idx)
        );
      } else {
        this.strokeArc(
          x.getItem(idx),
          y.getItem(idx),
          radius.getItem(idx),
          startAngle.getItem(idx),
          endAngle.getItem(idx),
          anticlockwise.getItem(idx)
        );
      }
    }
    this.ctx.restore();
  }

  drawStyledPolygonOrLineSegments(
    args: any[],
    buffers: any,
    fill: boolean,
    close: boolean
  ) {
    const numPolygons = args[0];
    const points = getArg(args[1], buffers);
    const sizes = getArg(args[2], buffers);
    const colors = getArg(args[3], buffers);
    const alpha = getArg(args[4], buffers);

    this.ctx.save();

    let start = 0;
    for (let idx = 0; idx < numPolygons; ++idx) {
      // get color for this circle
      const ci = 3 * idx;
      const color = `rgba(${colors.getItem(ci)}, ${colors.getItem(
        ci + 1
      )}, ${colors.getItem(ci + 2)}, ${alpha.getItem(idx)})`;
      this.setStyle(color, fill);

      // start / stop in the points array fr this polygon
      const size = sizes.getItem(idx) * 2;
      const stop = start + size;

      // Move to the first point, then create lines between points
      this.ctx.beginPath();
      this.ctx.moveTo(points.getItem(start), points.getItem(start + 1));

      // draw all points of the polygon (except start)
      for (let idp = start + 2; idp < stop; idp += 2) {
        this.ctx.lineTo(points.getItem(idp), points.getItem(idp + 1));
      }
      start = stop;
      if (close) {
        this.ctx.closePath();
      }
      fill ? this.ctx.fill() : this.ctx.stroke();
    }
    this.ctx.restore();
  }

  drawPolygonOrLineSegments(
    args: any[],
    buffers: any,
    fill: boolean,
    close: boolean
  ) {
    const numPolygons = args[0];
    const points = getArg(args[1], buffers);
    const sizes = getArg(args[2], buffers);

    let start = 0;
    for (let idx = 0; idx < numPolygons; ++idx) {
      // start / stop in the points array fr this polygon
      const size = sizes.getItem(idx) * 2;
      const stop = start + size;

      // Move to the first point, then create lines between points
      this.ctx.beginPath();
      this.ctx.moveTo(points.getItem(start), points.getItem(start + 1));

      // draw all points of the polygon (except start)
      for (let idp = start + 2; idp < stop; idp += 2) {
        this.ctx.lineTo(points.getItem(idp), points.getItem(idp + 1));
      }
      start = stop;
      if (close) {
        this.ctx.closePath();
      }
      fill ? this.ctx.fill() : this.ctx.stroke();
    }
  }

  strokeLine(args: any[], buffers: any) {
    this.ctx.beginPath();
    this.ctx.moveTo(args[0], args[1]);
    this.ctx.lineTo(args[2], args[3]);
    this.ctx.stroke();

    this.ctx.closePath();
  }

  strokeLines(args: any[], buffers: any) {
    this.ctx.beginPath();
    const points = getArg(args[0], buffers);

    // Move to the first point, then create lines between points
    this.ctx.moveTo(points.getItem(0), points.getItem(1));
    for (let idx = 2; idx < points.length; idx += 2) {
      this.ctx.lineTo(points.getItem(idx), points.getItem(idx + 1));
    }

    this.ctx.stroke();
    this.ctx.closePath();
  }

  fillPolygon(args: any[], buffers: any) {
    this.ctx.beginPath();
    const points = getArg(args[0], buffers);

    // Move to the first point, then create lines between points
    this.ctx.moveTo(points.getItem(0), points.getItem(1));
    for (let idx = 2; idx < points.length; idx += 2) {
      this.ctx.lineTo(points.getItem(idx), points.getItem(idx + 1));
    }

    this.ctx.closePath();
    this.ctx.fill();
  }

  strokePolygon(args: any[], buffers: any) {
    this.ctx.beginPath();
    const points = getArg(args[0], buffers);

    // Move to the first point, then create lines between points
    this.ctx.moveTo(points.getItem(0), points.getItem(1));
    for (let idx = 2; idx < points.length; idx += 2) {
      this.ctx.lineTo(points.getItem(idx), points.getItem(idx + 1));
    }

    this.ctx.closePath();
    this.ctx.stroke();
  }

  async fillPath(args: any[], buffers: any) {
    const [serializedPath] = args;

    const path = await unpack_models(serializedPath, this.widget_manager);

    this.ctx.fill(path.value);
  }

  async drawImage(args: any[], buffers: any) {
    const [serializedImage, x, y, width, height] = args;

    const image = await unpack_models(serializedImage, this.widget_manager);

    if (image instanceof CanvasModel || image instanceof MultiCanvasModel) {
      this._drawImage(image.canvas, x, y, width, height);
      return;
    }

    if (image.get('_model_name') == 'ImageModel') {
      const img = await createImageFromWidget(image);
      this._drawImage(img, x, y, width, height);
    }
  }

  private _drawImage(
    image: HTMLCanvasElement | HTMLImageElement,
    x: number,
    y: number,
    width: number | undefined,
    height: number | undefined
  ) {
    if (width === undefined || height === undefined) {
      this.ctx.drawImage(image, x, y);
    } else {
      this.ctx.drawImage(image, x, y, width, height);
    }
  }

  putImageData(args: any[], buffers: any) {
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

  async setAttr(attr: number, value: any) {
    if (typeof value === 'string' && value.startsWith('IPY')) {
      const widgetModel: GradientModel = await unpack_models(
        value,
        this.widget_manager
      );
      value = widgetModel.value;
    }

    (this.ctx as any)[CanvasModel.ATTRS[attr]] = value;
  }

  clearCanvas() {
    this.forEachView((view: CanvasView) => {
      view.clear();
    });
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  executeCommand(name: string, args: any[] = []) {
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
    this.canvas.setAttribute('width', this.get('width'));
    this.canvas.setAttribute('height', this.get('height'));
  }

  private async syncImageData() {
    if (!this.get('sync_image_data')) {
      return;
    }

    const bytes = await toBytes(this.canvas);

    this.set('image_data', bytes);
    this.save_changes();
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

export class RoughCanvasModel extends CanvasModel {
  static ROUGH_ATTRS: string[] = new Array(100).concat([
    'roughFillStyle',
    'roughness',
    'bowing'
  ]);

  defaults() {
    return { ...super.defaults(), _model_name: RoughCanvasModel.model_name };
  }

  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    this.roughCanvas = new RoughCanvas(this.canvas);
  }

  fillRect(x: number, y: number, width: number, height: number) {
    this.roughCanvas.rectangle(x, y, width, height, this.getRoughFillStyle());
  }

  strokeRect(x: number, y: number, width: number, height: number) {
    this.roughCanvas.rectangle(x, y, width, height, this.getRoughStrokeStyle());
  }

  fillCircle(x: number, y: number, radius: number) {
    this.roughCanvas.circle(x, y, 2 * radius, this.getRoughFillStyle());
  }

  strokeCircle(x: number, y: number, radius: number) {
    this.roughCanvas.circle(x, y, 2 * radius, this.getRoughStrokeStyle());
  }

  strokeLine(args: any[], buffers: any) {
    this.roughCanvas.line(
      args[0],
      args[1],
      args[2],
      args[3],
      this.getRoughStrokeStyle()
    );
  }

  strokeLines(args: any[], buffers: any) {
    const points = getArg(args[0], buffers);

    const polygon: [number, number][] = [];
    for (let idx = 0; idx < points.length; idx += 2) {
      polygon.push([points.getItem(idx), points.getItem(idx + 1)]);
    }

    this.roughCanvas.linearPath(polygon, this.getRoughStrokeStyle());
  }

  async fillPath(args: any[], buffers: any) {
    const [serializedPath] = args;

    const path = await unpack_models(serializedPath, this.widget_manager);

    this.roughCanvas.path(path.get('value'), this.getRoughFillStyle());
  }

  fillArc(
    x: number,
    y: number,
    radius: number,
    startAngle: number,
    endAngle: number,
    anticlockwise: boolean
  ) {
    const ellipseSize = 2 * radius;

    // The following is needed because roughjs does not allow a clockwise draw
    const start = anticlockwise ? endAngle : startAngle;
    const end = anticlockwise ? startAngle + 2 * Math.PI : endAngle;

    this.roughCanvas.arc(
      x,
      y,
      ellipseSize,
      ellipseSize,
      start,
      end,
      true,
      this.getRoughFillStyle()
    );
  }

  strokeArc(
    x: number,
    y: number,
    radius: number,
    startAngle: number,
    endAngle: number,
    anticlockwise: boolean
  ) {
    const ellipseSize = 2 * radius;

    // The following is needed because roughjs does not allow a clockwise draw
    const start = anticlockwise ? endAngle : startAngle;
    const end = anticlockwise ? startAngle + 2 * Math.PI : endAngle;

    this.roughCanvas.arc(
      x,
      y,
      ellipseSize,
      ellipseSize,
      start,
      end,
      false,
      this.getRoughStrokeStyle()
    );
  }

  fillPolygon(args: any[], buffers: any) {
    const points = getArg(args[0], buffers);

    const polygon: [number, number][] = [];
    for (let idx = 0; idx < points.length; idx += 2) {
      polygon.push([points.getItem(idx), points.getItem(idx + 1)]);
    }

    this.roughCanvas.polygon(polygon, this.getRoughFillStyle());
  }

  strokePolygon(args: any[], buffers: any) {
    const points = getArg(args[0], buffers);

    const polygon: [number, number][] = [];
    for (let idx = 0; idx < points.length; idx += 2) {
      polygon.push([points.getItem(idx), points.getItem(idx + 1)]);
    }

    this.roughCanvas.polygon(polygon, this.getRoughStrokeStyle());
  }

  async setAttr(attr: number, value: any) {
    if (RoughCanvasModel.ROUGH_ATTRS[attr]) {
      (this as any)[RoughCanvasModel.ROUGH_ATTRS[attr]] = value;

      return;
    }

    await super.setAttr(attr, value);
  }

  private getRoughFillStyle() {
    const fill = this.ctx.fillStyle as string;
    const lineWidth = this.ctx.lineWidth;

    return {
      fill,
      fillStyle: this.roughFillStyle,
      fillWeight: lineWidth / 2,
      hachureGap: lineWidth * 4,
      curveStepCount: 18,
      strokeWidth: 0.001, // This is to ensure there is no stroke,
      roughness: this.roughness,
      bowing: this.bowing
    };
  }

  private getRoughStrokeStyle() {
    const stroke = this.ctx.strokeStyle as string;
    const lineWidth = this.ctx.lineWidth;

    return {
      stroke,
      strokeWidth: lineWidth,
      roughness: this.roughness,
      bowing: this.bowing,
      curveStepCount: 18
    };
  }

  static model_name = 'RoughCanvasModel';

  roughCanvas: RoughCanvas;

  roughFillStyle: string = 'hachure';
  roughness: number = 1;
  bowing: number = 1;
}

export class CanvasView extends DOMWidgetView {
  render() {
    this.ctx = getContext(this.el);

    this.resizeCanvas();
    this.model.on_some_change(['width', 'height'], this.resizeCanvas, this);

    this.el.addEventListener('mousemove', {
      handleEvent: this.onMouseMove.bind(this)
    });
    this.el.addEventListener('mousedown', {
      handleEvent: this.onMouseDown.bind(this)
    });
    this.el.addEventListener('mouseup', {
      handleEvent: this.onMouseUp.bind(this)
    });
    this.el.addEventListener('mouseout', {
      handleEvent: this.onMouseOut.bind(this)
    });
    this.el.addEventListener('touchstart', {
      handleEvent: this.onTouchStart.bind(this)
    });
    this.el.addEventListener('touchend', {
      handleEvent: this.onTouchEnd.bind(this)
    });
    this.el.addEventListener('touchmove', {
      handleEvent: this.onTouchMove.bind(this)
    });
    this.el.addEventListener('touchcancel', {
      handleEvent: this.onTouchCancel.bind(this)
    });
    this.el.addEventListener('keydown', {
      handleEvent: this.onKeyDown.bind(this)
    });

    this.el.setAttribute('tabindex', '0');

    this.updateCanvas();
  }

  clear() {
    this.ctx.clearRect(0, 0, this.el.width, this.el.height);
  }

  updateCanvas() {
    this.clear();
    this.ctx.drawImage(this.model.canvas, 0, 0);
  }

  protected resizeCanvas() {
    this.el.setAttribute('width', this.model.get('width'));
    this.el.setAttribute('height', this.model.get('height'));
  }

  private onMouseMove(event: MouseEvent) {
    this.model.send({ event: 'mouse_move', ...this.getCoordinates(event) }, {});
  }

  private onMouseDown(event: MouseEvent) {
    // Bring focus to the canvas element, so keyboard events can be triggered
    this.el.focus();

    this.model.send({ event: 'mouse_down', ...this.getCoordinates(event) }, {});
  }

  private onMouseUp(event: MouseEvent) {
    this.model.send({ event: 'mouse_up', ...this.getCoordinates(event) }, {});
  }

  private onMouseOut(event: MouseEvent) {
    this.model.send({ event: 'mouse_out', ...this.getCoordinates(event) }, {});
  }

  private onTouchStart(event: TouchEvent) {
    const touches: Touch[] = Array.from(event.touches);
    this.model.send(
      {
        event: 'touch_start',
        touches: touches.map(this.getCoordinates.bind(this))
      },
      {}
    );
  }

  private onTouchEnd(event: TouchEvent) {
    const touches: Touch[] = Array.from(event.touches);
    this.model.send(
      {
        event: 'touch_end',
        touches: touches.map(this.getCoordinates.bind(this))
      },
      {}
    );
  }

  private onTouchMove(event: TouchEvent) {
    const touches: Touch[] = Array.from(event.touches);
    this.model.send(
      {
        event: 'touch_move',
        touches: touches.map(this.getCoordinates.bind(this))
      },
      {}
    );
  }

  private onTouchCancel(event: TouchEvent) {
    const touches: Touch[] = Array.from(event.touches);
    this.model.send(
      {
        event: 'touch_cancel',
        touches: touches.map(this.getCoordinates.bind(this))
      },
      {}
    );
  }

  private onKeyDown(event: KeyboardEvent) {
    event.preventDefault();
    event.stopPropagation();

    this.model.send(
      {
        event: 'key_down',
        key: event.key,
        shift_key: event.shiftKey,
        ctrl_key: event.ctrlKey,
        meta_key: event.metaKey
      },
      {}
    );
  }

  protected getCoordinates(event: MouseEvent | Touch) {
    const rect = this.el.getBoundingClientRect();

    const x = (this.el.width * (event.clientX - rect.left)) / rect.width;
    const y = (this.el.height * (event.clientY - rect.top)) / rect.height;

    return { x, y };
  }

  get tagName(): string {
    return 'canvas';
  }

  el: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;

  model: CanvasModel | MultiCanvasModel;
}

export class MultiCanvasModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: MultiCanvasModel.model_name,
      _model_module: MultiCanvasModel.model_module,
      _model_module_version: MultiCanvasModel.model_module_version,
      _view_name: MultiCanvasModel.view_name,
      _view_module: MultiCanvasModel.view_module,
      _view_module_version: MultiCanvasModel.view_module_version,
      _canvases: [],
      sync_image_data: false,
      image_data: null,
      width: 700,
      height: 500
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    _canvases: { deserialize: unpack_models as any },
    image_data: {
      serialize: (bytes: Uint8ClampedArray) => {
        return new DataView(bytes.buffer.slice(0));
      }
    }
  };

  initialize(attributes: any, options: any) {
    super.initialize(attributes, options);

    this.canvas = document.createElement('canvas');
    this.ctx = getContext(this.canvas);

    this.resizeCanvas();

    this.on_some_change(['width', 'height'], this.resizeCanvas, this);
    this.on('change:_canvases', this.updateCanvasModels.bind(this));
    this.on('change:sync_image_data', this.syncImageData.bind(this));

    this.updateCanvasModels();
  }

  get canvasModels(): CanvasModel[] {
    return this.get('_canvases');
  }

  private updateCanvasModels() {
    // TODO: Remove old listeners
    for (const canvasModel of this.canvasModels) {
      canvasModel.on('new-frame', this.updateCanvas, this);
    }

    this.updateCanvas();
  }

  private updateCanvas() {
    this.ctx.clearRect(0, 0, this.get('width'), this.get('height'));

    for (const canvasModel of this.canvasModels) {
      this.ctx.drawImage(canvasModel.canvas, 0, 0);
    }

    this.forEachView((view: MultiCanvasView) => {
      view.updateCanvas();
    });

    this.syncImageData();
  }

  private resizeCanvas() {
    this.canvas.setAttribute('width', this.get('width'));
    this.canvas.setAttribute('height', this.get('height'));
  }

  private async syncImageData() {
    if (!this.get('sync_image_data')) {
      return;
    }

    const bytes = await toBytes(this.canvas);

    this.set('image_data', bytes);
    this.save_changes();
  }

  private forEachView(callback: (view: MultiCanvasView) => void) {
    for (const view_id in this.views) {
      this.views[view_id].then((view: MultiCanvasView) => {
        callback(view);
      });
    }
  }

  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;

  views: Dict<Promise<MultiCanvasView>>;

  static model_name = 'MultiCanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'MultiCanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}

export class MultiCanvasView extends CanvasView {
  model: MultiCanvasModel;
}
