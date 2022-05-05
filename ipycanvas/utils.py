"""Binary module."""
from io import BytesIO

from PIL import Image as PILImage

import numpy as np

try:
    import orjson

    ORJSON_AVAILABLE = True
except ImportError:
    import json

    ORJSON_AVAILABLE = False


def image_bytes_to_array(im_bytes):
    """Turn raw image bytes into a NumPy array."""
    im_file = BytesIO(im_bytes)

    im = PILImage.open(im_file)

    return np.array(im)


def binary_image(ar, quality=75):
    f = BytesIO()
    PILImage.fromarray(ar.astype(np.uint8), "RGB" if ar.shape[2] == 3 else "RGBA").save(
        f, "JPEG", quality=quality
    )
    return f.getvalue()


def array_to_binary(ar):
    """Turn a NumPy array into a binary buffer."""
    # Unsupported int64 array JavaScript side
    if ar.dtype == np.int64:
        ar = ar.astype(np.int32)

    # Unsupported float16 array JavaScript side
    if ar.dtype == np.float16:
        ar = ar.astype(np.float32)

    # make sure it's contiguous
    if not ar.flags["C_CONTIGUOUS"]:
        ar = np.ascontiguousarray(ar)

    return {"shape": ar.shape, "dtype": str(ar.dtype)}, memoryview(ar)


def populate_args(arg, args, buffers):
    if isinstance(arg, (list, np.ndarray)):
        arg_metadata, arg_buffer = array_to_binary(np.asarray(arg))
        arg_metadata["idx"] = len(buffers)

        args.append(arg_metadata)
        buffers.append(arg_buffer)
    else:
        args.append(arg)


def commands_to_buffer(commands):
    # Turn the commands list into a binary buffer
    if ORJSON_AVAILABLE:
        return array_to_binary(
            np.frombuffer(
                bytes(orjson.dumps(commands, option=orjson.OPT_SERIALIZE_NUMPY)),
                dtype=np.uint8,
            )
        )
    else:
        return array_to_binary(
            np.frombuffer(bytes(json.dumps(commands), encoding="utf8"), dtype=np.uint8)
        )
