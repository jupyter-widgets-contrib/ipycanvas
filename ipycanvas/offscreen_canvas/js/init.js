


OffscreenCanvasRenderingContext2D.prototype.strokeLine = function (x1, y1, x2, y2) {
    this.beginPath();
    this.moveTo(x1, y1);
    this.lineTo(x2, y2);
    this.stroke();
};  

OffscreenCanvasRenderingContext2D.prototype.fillCircle = function (x, y, radius) {
    this.beginPath();
    this.arc(x, y, radius, 0, 2 * Math.PI);
    this.fill();
};

OffscreenCanvasRenderingContext2D.prototype.strokeCircle = function (x, y, radius) {
    this.beginPath();
    this.arc(x, y, radius, 0, 2 * Math.PI); 
    this.stroke();
};

OffscreenCanvasRenderingContext2D.prototype.fillArc = function (x, y, radius, startAngle, endAngle, counterClockwise) {
    this.beginPath();
    this.arc(x, y, radius, startAngle, endAngle, counterClockwise);
    this.fill();
};

OffscreenCanvasRenderingContext2D.prototype.strokeArc = function (x, y, radius, startAngle, endAngle, counterClockwise) {
    this.beginPath();
    this.arc(x, y, radius, startAngle, endAngle, counterClockwise);
    this.stroke();
};

OffscreenCanvasRenderingContext2D.prototype.fillPolygon = function (n_points, points) {
    this.beginPath();
    this.moveTo(points[0], points[1]);
    for (let i = 1; i < n_points; i++) {
        this.lineTo(points[i * 2], points[i * 2 + 1]);
    }
    this.closePath();
    this.fill();
};

OffscreenCanvasRenderingContext2D.prototype.strokePolygon = function (n_points, points) {
    this.beginPath();
    this.moveTo(points[0], points[1]);
    for (let i = 1; i < n_points; i++) {
        this.lineTo(points[i * 2], points[i * 2 + 1]);
    }
    this.closePath();
    this.stroke();
};


OffscreenCanvasRenderingContext2D.prototype._styledCircles = function ( x, y, radius, color, alpha, sizes, fill) {
    const xx = new ScalarBatchAccessor(x, sizes[0]);
    const yy = new ScalarBatchAccessor(y, sizes[1]);
    const rr = new ScalarBatchAccessor(radius, sizes[2]);
    const cc = new ColorBatchAccessor(color, sizes[3], alpha, sizes[4]);

    // get the the longest array size
    const n_items = largest_value(sizes, 5);

    if(fill) {
        for (let i = 0; i < n_items; i++) {
            this.fillStyle = cc.get(i);
            this.beginPath();
            this.arc(xx.get(i), yy.get(i), rr.get(i), 0, 2 * Math.PI);
            this.fill();

        }
    }
    else {
        for (let i = 0; i < n_items; i++) {
            const style = cc.get(i);
            this.strokeStyle = style;
            this.beginPath();
            this.arc(xx.get(i), yy.get(i), rr.get(i), 0, 2 * Math.PI);
            this.stroke();
        }
    }
};

OffscreenCanvasRenderingContext2D.prototype.fillStyledCircles = function ( x, y, radius, color, alpha, sizes) {
    this._styledCircles(x, y, radius, color, alpha, sizes, true);
};

OffscreenCanvasRenderingContext2D.prototype.strokeStyledCircles = function ( x, y, radius, color, alpha, sizes) {
    this._styledCircles(x, y, radius, color, alpha, sizes, false);
};


OffscreenCanvasRenderingContext2D.prototype._circles = function ( x, y, radius, sizes, fill) {
    const xx = new ScalarBatchAccessor(x, sizes[0]);
    const yy = new ScalarBatchAccessor(y, sizes[1]);
    const rr = new ScalarBatchAccessor(radius, sizes[2]);

    // get the the longest array size
    const n_items = largest_value(sizes, 3);

    for (let i = 0; i < n_items; i++) {
        this.beginPath();
        this.arc(xx.get(i), yy.get(i), rr.get(i), 0, 2 * Math.PI);
        if (fill) {
            this.fill();
        } else {
            this.stroke();
        }
    }
};

OffscreenCanvasRenderingContext2D.prototype.fillCircles = function ( x, y, radius, sizes) {
    this._circles(x, y, radius, sizes, true);
};

OffscreenCanvasRenderingContext2D.prototype.strokeCircles = function ( x, y, radius, sizes) {
    this._circles(x, y, radius, sizes, false);
};




function largest_value(buffers, size) {
    let largest = 0;
    for (let i = 0; i < size; i++) {
        const value = buffers[i];   
        if (value > largest) {
            largest = value;
        }
    }
    return largest;
}

class ScalarBatchAccessor {
  constructor(typedArray, length) {
    if(length === 1) {
        this._v0 = typedArray[0];
        this.get = this._get_0;
    }
    else {
        this._array = typedArray;
        this.get = this._get_i;
    }
  }
  _get_i(index) {
    return this._array[index];
  }
  _get_0(index) {
    return this._v0
  }
}


class ColorBatchAccessor {
    constructor(
        colorArray,
        colorArrayLength,
        alphaArray,
        alphaArrayLength
    ) {
        this.colorArrayLength = colorArrayLength;
        this.alphaArrayLength = alphaArrayLength;
        this._colorArray = colorArray;
        this._alphaArray = alphaArray;
    }
    get(index) {
        const colorIndex = index < this.colorArrayLength ? index * 3 : 0;
        const alphaIndex = index < this.alphaArrayLength ? index : 0;
        return `rgba(${this._colorArray[colorIndex]}, ${this._colorArray[colorIndex + 1]}, ${this._colorArray[colorIndex + 2]}, ${this._alphaArray[alphaIndex]})`;
    }
}

//  mouse event handler factory
//  arr_mouse_state: [is_inside, is_down, x, y]
function reciver_factory(arr) {
    return {
        arr_mouse_state : arr,
        on_mouse_events: function(event, x, y) {

            if (event === "mouseenter") {
                this.arr_mouse_state[0] = 1;  // is_inside
                this.arr_mouse_state[1] = 0;  // is_down

                if (this.on_mouse_enter) {
                    this.on_mouse_enter(x, y);
                }

            } else if (event === "mouseleave") {
                this.arr_mouse_state[0] = 0;  // is_inside
                this.arr_mouse_state[1] = 0;  // is_down

                if (this.on_mouse_leave) {
                    this.on_mouse_leave(x, y);
                }

            } else if (event === "mousedown") {
                this.arr_mouse_state[1] = 1;  // is_down
                if (this.on_mouse_down) {
                    this.on_mouse_down(x, y);
                }

            } else if (event === "mouseup") {
                this.arr_mouse_state[1] = 0;  // is_down
                if (this.on_mouse_up) {
                    this.on_mouse_up(x, y);
                }
            }
            else if (event === "mousemove") {
                if (this.on_mouse_move) {
                    this.on_mouse_move(x, y);
                }
            }
            // always update the mouse position
            this.arr_mouse_state[2] = x;  // x position
            this.arr_mouse_state[3] = y;  // y position
        },
        // python functions that are accessible from
        // javacript need to be deleted
        cleanup : function() {
            if(reciver._cleanup_mouse_enter) {
                reciver._cleanup_mouse_enter.delete();
            }
            if(reciver._cleanup_mouse_leave) {
                reciver._cleanup_mouse_leave.delete();
            }
            if(reciver._cleanup_mouse_down) {
                reciver._cleanup_mouse_down.delete();
            }
            if(reciver._cleanup_mouse_up) {
                reciver._cleanup_mouse_up.delete();
            }
            if(reciver._cleanup_mouse_move) {
                reciver._cleanup_mouse_move.delete();
            }
        }
    }
}


globalThis["_ipycanvas"] = {
    reciver_factory: reciver_factory
};