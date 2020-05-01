function getTypedArray(dataview: any, metadata: any) {
  switch (metadata.dtype) {
    case 'int8':
      return new Int8Array(dataview.buffer);
      break;
    case 'int16':
      return new Int16Array(dataview.buffer);
      break;
    case 'int32':
      return new Int32Array(dataview.buffer);
      break;
    case 'float32':
      return new Float32Array(dataview.buffer);
      break;
    case 'float64':
      return new Float64Array(dataview.buffer);
      break;
    default:
      throw 'Unknown dtype ' + metadata.dtype;
      break;
  }
}

// Scalar type
type Scalar = null | boolean | number | string;

namespace Scalar {
  export
  function isScalar(x: any): x is Scalar {
      return x === null || typeof x === "boolean" || typeof x === "number" || typeof x === "string";
  }
}

type TypedArray = Int8Array | Uint8Array | Int16Array | Uint16Array | Int32Array | Uint32Array | Uint8ClampedArray | Float32Array | Float64Array;

// Buffered argument
export
abstract class Arg {
  abstract getItem(idx: number) : any;

  length: number;
}

class ScalarArg extends Arg {
  constructor(value: Scalar) {
    super();

    this.value = value;
    this.length = Infinity;
  }

  getItem(idx: number) : any {
    return this.value;
  }

  value: Scalar;
}

class BufferArg extends Arg {
  constructor(bufferMetadata: any, buffer: any[]) {
    super();

    this.value = getTypedArray(buffer, bufferMetadata);
    this.length = this.value.length;
  }

  getItem(idx: number) : any {
    return this.value[idx];
  }

  value: TypedArray;
}

export
function getArg(metadata: any, buffers: any) : Arg {
  if (Scalar.isScalar(metadata)) {
    return new ScalarArg(metadata);
  }

  if (metadata['idx'] !== undefined) {
    return new BufferArg(metadata, buffers[metadata['idx']])
  }

  throw 'Could not process argument ' + metadata;
}

export
async function toBlob(canvas: HTMLCanvasElement) : Promise<Blob> {
  return new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob == null) {
        return reject('Unable to create blob');
      }

      resolve(blob);
    });
  });
}

export
async function toBytes(canvas: HTMLCanvasElement) : Promise<Uint8ClampedArray> {
  const blob = await toBlob(canvas);

  return new Promise<Uint8ClampedArray>((resolve, reject) => {
    const reader = new FileReader();

    reader.onloadend = () => {
        if (typeof reader.result == 'string' || reader.result == null) {
          return reject('Unable to read blob');
        }

        const bytes = new Uint8ClampedArray(reader.result);
        resolve(bytes);
    };
    reader.readAsArrayBuffer(blob);
  });
}

export
async function fromBytes(array: Uint8ClampedArray) : Promise<HTMLImageElement> {
  const blob = new Blob([array]);

  return new Promise<HTMLImageElement>((resolve, reject) => {
    const img = new Image();

    img.onload = () => {
      resolve(img);
    }

    img.src = URL.createObjectURL(blob);
  });
}
