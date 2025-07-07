


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
            this.strokeStyle = cc.get(i);
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
        if (colorArrayLength === 1 && alphaArrayLength === 1) {
            this._rgba = `rgba(${colorArray[0]}, ${colorArray[1]}, ${colorArray[2]}, ${alphaArray[0]})`;
            this.get = this._get_0;
        }
        else {
            this._colorArray = colorArray;
            this._alphaArray = alphaArray;
            this.get = this._get_i;
        }
    }
    _get_i(index) {
        const colorIndex = index * 3;
        const alphaIndex = index < this._alphaArray.length ? index : 0;
        return `rgba(${this._colorArray[colorIndex]}, ${this._colorArray[colorIndex + 1]}, ${this._colorArray[colorIndex + 2]}, ${this._alphaArray[alphaIndex]})`;
    }
}

// store class in global scope
globalThis.ScalarBatchAccessor = ScalarBatchAccessor;
globalThis.ColorBatchAccessor = ColorBatchAccessor;
