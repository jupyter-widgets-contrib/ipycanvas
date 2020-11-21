"""Binary module."""
from io import BytesIO

from PIL import Image as PILImage

import numpy as np

import orjson


def image_bytes_to_array(im_bytes):
    """Turn raw image bytes into a NumPy array."""
    im_file = BytesIO(im_bytes)

    im = PILImage.open(im_file)

    return np.array(im)


def binary_image(ar):
    """Turn a NumPy array representing an array of pixels into a binary buffer."""
    if ar is None:
        return None
    if ar.dtype != np.uint8:
        ar = ar.astype(np.uint8)
    if ar.ndim == 1:
        ar = ar[np.newaxis, :]
    if ar.ndim == 2:
        # extend grayscale to RGBA
        add_alpha = np.full((ar.shape[0], ar.shape[1], 4), 255, dtype=np.uint8)
        add_alpha[:, :, :3] = np.repeat(ar[:, :, np.newaxis], repeats=3, axis=2)
        ar = add_alpha
    if ar.ndim != 3:
        raise ValueError("Please supply an RGBA array with shape (width, height, 4).")
    if ar.shape[2] != 4 and ar.shape[2] == 3:
        add_alpha = np.full((ar.shape[0], ar.shape[1], 4), 255, dtype=np.uint8)
        add_alpha[:, :, :3] = ar
        ar = add_alpha
    if not ar.flags["C_CONTIGUOUS"]:  # make sure it's contiguous
        ar = np.ascontiguousarray(ar, dtype=np.uint8)
    return {'shape': ar.shape, 'dtype': str(ar.dtype)}, memoryview(ar)


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

    return {'shape': ar.shape, 'dtype': str(ar.dtype)}, memoryview(ar)


def populate_args(arg, args, buffers):
    if isinstance(arg, (list, np.ndarray)):
        arg_metadata, arg_buffer = array_to_binary(np.asarray(arg))
        arg_metadata['idx'] = len(buffers)

        args.append(arg_metadata)
        buffers.append(arg_buffer)
    else:
        args.append(arg)


def commands_to_buffer(commands):
    # Turn the commands list into a binary buffer
    return array_to_binary(np.frombuffer(
        bytes(orjson.dumps(commands, option=orjson.OPT_SERIALIZE_NUMPY)),
        dtype=np.uint8)
    )
