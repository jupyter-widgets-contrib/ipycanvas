import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

import { MODULE_NAME, MODULE_VERSION } from './version';

// MODEL
 class MyCanvasModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: MyCanvasModel.model_name,
      _model_module: MyCanvasModel.model_module,
      _model_module_version: MyCanvasModel.model_module_version,
      _view_name: MyCanvasModel.view_name,
      _view_module: MyCanvasModel.view_module,
      _view_module_version: MyCanvasModel.view_module_version,
      width: 300,
      height: 150,
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
  };

  static model_name = 'MyCanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'MyCanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}

// VIEW
class MyCanvasView extends DOMWidgetView {
  canvasEl: HTMLCanvasElement;

  render(): void {
    this.canvasEl = document.createElement('canvas');
    this.el.appendChild(this.canvasEl);

    this.updateCanvasSize();

    this.model.on('change:width', this.updateCanvasSize, this);
    this.model.on('change:height', this.updateCanvasSize, this);
  }

  updateCanvasSize(): void {
    const width = this.model.get('width');
    const height = this.model.get('height');
    this.canvasEl.width = width;
    this.canvasEl.height = height;
    this.canvasEl.style.width = `${width}px`;
    this.canvasEl.style.height = `${height}px`;
  }
}

export { MyCanvasModel, MyCanvasView };