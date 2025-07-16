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
      _width: 300,
      _height: 150,
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
  el: HTMLCanvasElement;

  // @ts-ignore: 2611
  get tagName(): string {
    return 'canvas';
  }
  
  render(): void {
    // this.canvas = document.createElement('canvas');
    // this.el.appendChild(this.canvas);
    

    const _canvas_name = () => `_canvas_${this.model.get('_name')}`;
    const _receiver_name = () => `_canvas_receiver_${this.model.get('_name')}`;

    this.setCanvasSize();

    // magic here!
    const offscreen: OffscreenCanvas = this.el.transferControlToOffscreen();
    (globalThis as any).storeAsGlobal(offscreen, _canvas_name());
    

    const that = this;

    async function sendMouseEvent(event : MouseEvent): Promise<void> {

        const rect = that.el.getBoundingClientRect();
        try{
            await (globalThis as any).callGlobalReceiver(_receiver_name(), "on_mouse_events",
                event.type,
                event.clientX - rect.left,
                event.clientY - rect.top,
            );
        } 
        // we want to remove all event listeners if the receiver is not defined
        catch (e) {
            console.error("Error while sending mouse event, removing listeners:", e);
            (that as any).el.removeEventListener("mousedown", sendMouseEvent);
            (that as any).el.removeEventListener("mouseup",   sendMouseEvent);
            (that as any).el.removeEventListener("mousemove", sendMouseEvent);        
            (that as any).el.removeEventListener("mouseenter", sendMouseEvent);
            (that as any).el.removeEventListener("mouseleave", sendMouseEvent);
        }

    };

    
    this.el.addEventListener("mousedown", sendMouseEvent);
    this.el.addEventListener("mouseup",   sendMouseEvent);
    this.el.addEventListener("mousemove", sendMouseEvent);
    this.el.addEventListener("mouseenter", sendMouseEvent);
    this.el.addEventListener("mouseleave", sendMouseEvent);




  }

  // note that we cannot update the canvas here size once its transferred to the offscreen context
  // (the canvas **can** be resized after beeing transferred, but only **on** the transfered object,
  // ie in the worker)
  setCanvasSize(): void {
    const width = this.model.get('_width');
    const height = this.model.get('_height');
    this.el.width = width;
    this.el.height = height;
  }
}

export { OffscreenCanvasModel, OffscreenCanvasView };