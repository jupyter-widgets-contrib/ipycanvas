


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

OffscreenCanvasRenderingContext2D.prototype.fillAndStrokePolygon = function (n_points, points) {
    this.beginPath();
    this.moveTo(points[0], points[1]);
    for (let i = 1; i < n_points; i++) {
        this.lineTo(points[i * 2], points[i * 2 + 1]);
    }
    this.closePath();
    this.fill();
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



// batch api for rects
OffscreenCanvasRenderingContext2D.prototype._rects = function (x, y, width, height, sizes, fill) {
    const xx = new ScalarBatchAccessor(x, sizes[0]);
    const yy = new ScalarBatchAccessor(y, sizes[1]);
    const ww = new ScalarBatchAccessor(width, sizes[2]);
    const hh = new ScalarBatchAccessor(height, sizes[3]);

    // get the the longest array size
    const n_items = largest_value(sizes, 4);

    for (let i = 0; i < n_items; i++) {
        if (fill) {
            this.fillRect(xx.get(i), yy.get(i), ww.get(i), hh.get(i));
        } else {
            this.strokeRect(xx.get(i), yy.get(i), ww.get(i), hh.get(i));
        }
    }
};

OffscreenCanvasRenderingContext2D.prototype.fillRects = function (x, y, width, height, sizes) {
    this._rects(x, y, width, height, sizes, true);
};
OffscreenCanvasRenderingContext2D.prototype.strokeRects = function (x, y, width, height, sizes) {
    this._rects(x, y, width, height, sizes, false);
};

// styled rects
OffscreenCanvasRenderingContext2D.prototype._styledRects = function (x, y, width, height, color, alpha, sizes, fill) {
    const xx = new ScalarBatchAccessor(x, sizes[0]);
    const yy = new ScalarBatchAccessor(y, sizes[1]);
    const ww = new ScalarBatchAccessor(width, sizes[2]);
    const hh = new ScalarBatchAccessor(height, sizes[3]);
    const cc = new ColorBatchAccessor(color, sizes[4], alpha, sizes[5]);
    // get the the longest array size
    const n_items = largest_value(sizes, 6);
    for (let i = 0; i < n_items; i++) {
        if (fill) {
            this.fillStyle = cc.get(i);
            this.fillRect(xx.get(i), yy.get(i), ww.get(i), hh.get(i));
        } else {
            this.strokeStyle = cc.get(i);
            this.strokeRect(xx.get(i), yy.get(i), ww.get(i), hh.get(i));
        }
    }
};

OffscreenCanvasRenderingContext2D.prototype.fillStyledRects = function (x, y, width, height, color, alpha, sizes) {
    this._styledRects(x, y, width, height, color, alpha, sizes, true);
};
OffscreenCanvasRenderingContext2D.prototype.strokeStyledRects = function (x, y, width, height, color, alpha, sizes) {
    this._styledRects(x, y, width, height, color, alpha, sizes, false);
};

// arc batch api
OffscreenCanvasRenderingContext2D.prototype._arcs = function (x, y, radius, startAngle, endAngle, sizes, counterClockwise, fill) {
    const xx = new ScalarBatchAccessor(x, sizes[0]);
    const yy = new ScalarBatchAccessor(y, sizes[1]);
    const rr = new ScalarBatchAccessor(radius, sizes[2]);
    const sa = new ScalarBatchAccessor(startAngle, sizes[3]);
    const ea = new ScalarBatchAccessor(endAngle, sizes[4]);

    const n_items = largest_value(sizes, 5);

    console.log(`n_items: ${n_items}, sizes: ${sizes}`);
    for (let i = 0; i < n_items; i++) {
        this.beginPath();
        
        console.log(`arc: x=${xx.get(i)}, y=${yy.get(i)}, r=${rr.get(i)}, sa=${sa.get(i)}, ea=${ea.get(i)}, cc=${counterClockwise}`);


        this.arc(xx.get(i), yy.get(i), rr.get(i), sa.get(i),
                 ea.get(i), counterClockwise);
        if (fill) {
            this.fill();
        } else {
            this.stroke();
        }
    }
};
OffscreenCanvasRenderingContext2D.prototype.fillArcs = function (x, y, radius, startAngle, endAngle, sizes, counterClockwise) {
    this._arcs(x, y, radius, startAngle, endAngle, sizes,  counterClockwise, true);
};
OffscreenCanvasRenderingContext2D.prototype.strokeArcs = function (x, y, radius  , startAngle, endAngle, sizes, counterClockwise) {
    this._arcs(x, y, radius, startAngle, endAngle, sizes, counterClockwise, false);
};  

// arc batch api with styled colors
OffscreenCanvasRenderingContext2D.prototype._styledArcs = function (x, y, radius, startAngle, endAngle, color, alpha, sizes, counterClockwise, fill) {
    const xx = new ScalarBatchAccessor(x, sizes[0]);
    const yy = new ScalarBatchAccessor(y, sizes[1]);
    const rr = new ScalarBatchAccessor(radius, sizes[2]);
    const sa = new ScalarBatchAccessor(startAngle, sizes[3]);
    const ea = new ScalarBatchAccessor(endAngle, sizes[4]);
    const cc = new ColorBatchAccessor(color, sizes[5], alpha, sizes[6]);
    // get the the longest array size
    const n_items = largest_value(sizes, 7);
    for (let i = 0; i < n_items; i++) {
        this.beginPath();
        this.arc(xx.get(i), yy.get(i), rr.get(i), sa.get(i),
                 ea.get(i), counterClockwise);
        if (fill) {
            this.fillStyle = cc.get(i);
            this.fill();
        } else {
            this.strokeStyle = cc.get(i);
            this.stroke();
        }
    }
};

OffscreenCanvasRenderingContext2D.prototype.fillStyledArcs = function (x, y, radius, startAngle, endAngle, color, alpha, sizes, counterClockwise) {
    this._styledArcs(x, y, radius, startAngle, endAngle, color, alpha, sizes, counterClockwise, true);
};
OffscreenCanvasRenderingContext2D.prototype.strokeStyledArcs = function (x, y, radius, startAngle, endAngle, color, alpha, sizes,counterClockwise) {
    this._styledArcs(x, y, radius, startAngle, endAngle, color, alpha, sizes, counterClockwise, false);
};


    
// polygon batch api
OffscreenCanvasRenderingContext2D.prototype._polygons = function (
    n_items,
    points,
    points_per_item,
    sizes,
    fill
) {
    console.log(`n_items: ${n_items}, sizes: ${sizes}`);
    const pp = new ScalarBatchAccessor(points, sizes[0]);
    const ppi = new ScalarBatchAccessor(points_per_item, sizes[1]);

    var acc = 0;
    for( let i = 0; i < n_items; i++) {
        const n_points = ppi.get(i);
        this.beginPath();
        this.moveTo(pp.get(acc), pp.get(acc + 1));
        for (let j = 1; j < n_points; j++) {
            this.lineTo(pp.get(acc + j * 2), pp.get(acc + j * 2 + 1));
        }
        this.closePath();
        if (fill) {
            this.fill();
        } else {
            this.stroke();
        }
        acc += n_points * 2;
    }
};

OffscreenCanvasRenderingContext2D.prototype.fillPolygons = function (
    n_items,
    points,
    points_per_item,
    sizes
) {
    this._polygons(n_items, points, points_per_item, sizes, true);
};  

OffscreenCanvasRenderingContext2D.prototype.strokePolygons = function (
    n_items,
    points,
    points_per_item,
    sizes
) {
    this._polygons(n_items, points, points_per_item, sizes, false);
};

// styled polygon batch api
OffscreenCanvasRenderingContext2D.prototype._styledPolygons = function (
    n_items,
    points,
    points_per_item,
    color,  
    alpha,
    sizes,
    fill
) {
    const pp = new ScalarBatchAccessor(points, sizes[0]);
    const ppi = new ScalarBatchAccessor(points_per_item, sizes[1]);
    const cc = new ColorBatchAccessor(color, sizes[2], alpha, sizes[3]);
    var acc = 0;
    for( let i = 0; i < n_items; i++) {
        const n_points = ppi.get(i);
        this.beginPath();
        this.moveTo(pp.get(acc), pp.get(acc + 1));
        for (let j = 1; j < n_points; j++) {
            this.lineTo(pp.get(acc + j * 2), pp.get(acc + j * 2 + 1));
        }
        this.closePath();
        if (fill) {
            this.fillStyle = cc.get(i);
            this.fill();    
        } else {
            this.strokeStyle = cc.get(i);
            this.stroke();
        }
        acc += n_points * 2;
    }
};

OffscreenCanvasRenderingContext2D.prototype.fillStyledPolygons = function (
    n_items,
    points,
    points_per_item,
    color,
    alpha,
    sizes
) {
    this._styledPolygons(n_items, points, points_per_item, color, alpha, sizes, true);
};
OffscreenCanvasRenderingContext2D.prototype.strokeStyledPolygons = function (
    n_items,
    points,
    points_per_item,
    color,
    alpha,      
    sizes
) {
    this._styledPolygons(n_items, points, points_per_item, color, alpha, sizes, false);
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
function receiver_factory(arr) {
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
            if(receiver._cleanup_mouse_enter) {
                receiver._cleanup_mouse_enter.delete();
            }
            if(receiver._cleanup_mouse_leave) {
                receiver._cleanup_mouse_leave.delete();
            }
            if(receiver._cleanup_mouse_down) {
                receiver._cleanup_mouse_down.delete();
            }
            if(receiver._cleanup_mouse_up) {
                receiver._cleanup_mouse_up.delete();
            }
            if(receiver._cleanup_mouse_move) {
                receiver._cleanup_mouse_move.delete();
            }
        }
    }
}


globalThis["_ipycanvas"] = {
    receiver_factory: receiver_factory
};