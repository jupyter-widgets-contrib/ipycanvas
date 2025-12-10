import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers
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
    ...DOMWidgetModel.serializers
  };

  static model_name = 'OffscreenCanvasModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'OffscreenCanvasView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
  static _name = '_canvas_0';
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
    this.el.setAttribute('tabindex', '0');
    // magic here!
    const offscreen: OffscreenCanvas = this.el.transferControlToOffscreen();
    (globalThis as any).storeAsGlobal(offscreen, _canvas_name());

    const that = this;

    // helper function to remove all listeners
    const removeAllListeners = () => {
      that.el.removeEventListener('mousedown', sendMouseEvent);
      that.el.removeEventListener('mouseup', sendMouseEvent);
      that.el.removeEventListener('mousemove', sendMouseEvent);
      that.el.removeEventListener('mouseenter', sendMouseEvent);
      that.el.removeEventListener('mouseleave', sendMouseEvent);
      that.el.removeEventListener('touchstart', sendTouchEvent);
      that.el.removeEventListener('touchend', sendTouchEvent);
      that.el.removeEventListener('touchmove', sendTouchEvent);
      that.el.removeEventListener('touchcancel', sendTouchEvent);
      that.el.removeEventListener('keydown', sendKeyboardEvent);
      that.el.removeEventListener('keyup', sendKeyboardEvent);
      that.el.removeEventListener('keypress', sendKeyboardEvent);
    };

    async function sendMouseEvent(event: MouseEvent): Promise<void> {
      if (event.type === 'mousedown') {
        that.el.focus();
      }

      const rect = that.el.getBoundingClientRect();
      const scaleX = that.el.width / rect.width;
      const scaleY = that.el.height / rect.height;
      try {
        await (globalThis as any).callGlobalReceiver(
          _receiver_name(),
          'on_mouse_events',
          event.type,
          (event.clientX - rect.left) * scaleX,
          (event.clientY - rect.top) * scaleY
        );
      } catch (e) {
        // we want to remove all event listeners if the receiver is not defined
        console.error(
          'Error while sending mouse event, removing listeners:',
          e
        );
        removeAllListeners();
      }
    }
    async function sendTouchEvent(event: TouchEvent): Promise<void> {
      const rect = that.el.getBoundingClientRect();
      const scaleX = that.el.width / rect.width;
      const scaleY = that.el.height / rect.height;
      try {
        for (let i = 0; i < event.changedTouches.length; i++) {
          const touch = event.changedTouches[i];
          await (globalThis as any).callGlobalReceiver(
            _receiver_name(),
            'on_touch_events',
            event.type,
            (touch.clientX - rect.left) * scaleX,
            (touch.clientY - rect.top) * scaleY,
            touch.identifier
          );
        }
      } catch (e) {
        // we want to remove all event listeners if the receiver is not defined
        console.error(
          'Error while sending touch event, removing listeners:',
          e
        );
        removeAllListeners();
      }
    }

    // keyboard events
    async function sendKeyboardEvent(event: KeyboardEvent): Promise<void> {
      event.preventDefault();
      event.stopPropagation();
      try {
        await (globalThis as any).callGlobalReceiver(
          _receiver_name(),
          'on_keyboard_events',
          event.type,
          event.key,
          event.ctrlKey,
          event.shiftKey,
          event.metaKey
        );
      } catch (e) {
        // we want to remove all event listeners if the receiver is not defined
        console.error(
          'Error while sending keyboard event, removing listeners:',
          e
        );
        removeAllListeners();
      }
    }

    // mouse events
    this.el.addEventListener('mousedown', sendMouseEvent);
    this.el.addEventListener('mouseup', sendMouseEvent);
    this.el.addEventListener('mousemove', sendMouseEvent);
    this.el.addEventListener('mouseenter', sendMouseEvent);
    this.el.addEventListener('mouseleave', sendMouseEvent);

    // wheel events
    this.el.addEventListener('wheel', async (event: WheelEvent) => {
      event.preventDefault();
      event.stopPropagation();
      const deltaY = event.deltaY;
      await (globalThis as any).callGlobalReceiver(
        _receiver_name(),
        'on_wheel_event',
        deltaY
      );
    });

    // touch events
    const opts = { passive: false };

    this.el.addEventListener('touchstart', e => sendTouchEvent(e), opts);
    this.el.addEventListener('touchend', e => sendTouchEvent(e), opts);
    this.el.addEventListener('touchcancel', e => sendTouchEvent(e), opts);
    
    this.el.addEventListener('touchmove', e => {
      e.preventDefault();      // IMPORTANT
      e.stopImmediatePropagation();
      sendTouchEvent(e);
    }, opts);
    
    // keyboard events
    this.el.addEventListener('keydown', sendKeyboardEvent);
    this.el.addEventListener('keyup', sendKeyboardEvent);
    this.el.addEventListener('keypress', sendKeyboardEvent);
  }

  // note that we cannot update the canvas here size once its transferred to the offscreen context
  setCanvasSize(): void {
    const width = this.model.get('_width');
    const height = this.model.get('_height');
    this.el.width = width;
    this.el.height = height;
  }
}

export { OffscreenCanvasModel, OffscreenCanvasView };
