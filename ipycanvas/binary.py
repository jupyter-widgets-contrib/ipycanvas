"""Binary module."""
import numpy as np


def array_to_binary(ar):
    """Turn a NumPy array into a binary buffer."""
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
    return ar.shape, memoryview(ar)
