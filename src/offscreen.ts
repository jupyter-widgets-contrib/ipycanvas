import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

import { MODULE_NAME, MODULE_VERSION } from './version';

// MODEL
 class OffscreenCanvasModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: OffscreenCanvasModel.model_name,
      _model_module: OffscreenCanvasModel.model_module,
      _model_module_version: OffscreenCanvasModel.model_module_version,
      _view_name: OffscreenCanvasModel.view_name,
      _view_module: OffscreenCanvasModel.view_module,
      _view_module_version: OffscreenCanvasModel.view_module_version,
      width: 300,
      height: 150,
      _name: OffscreenCanvasModel._name
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
  };

  static model_name = 'OffscreenCanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'OffscreenCanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
  static _name = "_canvas_0";
}

// VIEW
class OffscreenCanvasView extends DOMWidgetView {
  canvas: HTMLCanvasElement;

  render(): void {
    this.canvas = document.createElement('canvas');
    this.el.appendChild(this.canvas);


    const _canvas_name = () => `_canvas_${this.model.get('_name')}`;
    const _reciver_name = () => `_canvas_reciver_${this.model.get('_name')}`;

    // magic here!
    const offscreen: OffscreenCanvas = this.canvas.transferControlToOffscreen();
    (globalThis as any).storeAsGlobal(offscreen, _canvas_name());
    

    const that = this;

    async function sendMouseEvent(event : MouseEvent): Promise<void> {

        const rect = that.canvas.getBoundingClientRect();
        try{
            await (globalThis as any).callGlobalReciver(_reciver_name(), "on_mouse_events",
                event.type,
                event.clientX - rect.left,
                event.clientY - rect.top,
            );
        } 
        // we want to remove all event listeners if the reciver is not defined
        catch (e) {
            console.error("Error while sending mouse event, removing listeners:", e);
            (that as any).canvas.removeEventListener("mousedown", sendMouseEvent);
            (that as any).canvas.removeEventListener("mouseup",   sendMouseEvent);
            (that as any).canvas.removeEventListener("mousemove", sendMouseEvent);        
            (that as any).canvas.removeEventListener("mouseenter", sendMouseEvent);
            (that as any).canvas.removeEventListener("mouseleave", sendMouseEvent);
        }

    };

    
    this.canvas.addEventListener("mousedown", sendMouseEvent);
    this.canvas.addEventListener("mouseup",   sendMouseEvent);
    this.canvas.addEventListener("mousemove", sendMouseEvent);
    this.canvas.addEventListener("mouseenter", sendMouseEvent);
    this.canvas.addEventListener("mouseleave", sendMouseEvent);





    this.model.on('change:width', this.updateCanvasSize, this);
    this.model.on('change:height', this.updateCanvasSize, this);
  }


  updateCanvasSize(): void {
    const width = this.model.get('width');
    const height = this.model.get('height');
    this.canvas.width = width;
    this.canvas.height = height;
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
  }
}

export { OffscreenCanvasModel, OffscreenCanvasView };