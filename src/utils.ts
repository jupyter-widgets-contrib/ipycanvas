function getTypedArray(dataview: any, metadata: any) {
  switch (metadata.dtype) {
    case 'int32':
      return new Int32Array(dataview.buffer);
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
