import asyncio

import ipywidgets as widgets
import numpy as np
from ipycanvas import Canvas, hold_canvas


def game_of_life_demo():
    canvas = Canvas(width=920, height=540, layout=dict(width="920px", height="540px"))
    
    seed = widgets.IntSlider(value=7, min=0, max=9999, description="Seed")
    cell_px = widgets.IntSlider(value=8, min=4, max=18, description="Cell px")
    density = widgets.FloatSlider(value=0.22, min=0.05, max=0.6, step=0.01, readout_format=".2f", description="Density")
    speed_ms = widgets.IntSlider(value=80, min=20, max=400, step=10, description="Speed")
    alive_color = widgets.ColorPicker(value="#2f7e4a", description="Alive")
    bg_color = widgets.ColorPicker(value="#f3f7ee", description="Background")
    shape_dd = widgets.Dropdown(
        options=[
            "Single Cell",
            "Glider",
            "Blinker",
            "Toad",
            "Beacon",
            "LWSS",
            "Gosper Gun",
        ],
        value="Glider",
        description="Stamp",
    )
    
    start_btn = widgets.Button(description="Start", button_style="success")
    stop_btn = widgets.Button(description="Stop", button_style="warning")
    step_btn = widgets.Button(description="Step")
    random_btn = widgets.Button(description="Randomize", button_style="info")
    clear_btn = widgets.Button(description="Clear")
    
    state = {
        "running": False,
        "grid": None,
        "task": None,
        "generation": 0,
        "controls_dirty": True,
    }
    
    PATTERNS = {
        "Single Cell": np.array([[1]], dtype=bool),
        "Glider": np.array(
            [
                [0, 1, 0],
                [0, 0, 1],
                [1, 1, 1],
            ],
            dtype=bool,
        ),
        "Blinker": np.array([[1, 1, 1]], dtype=bool),
        "Toad": np.array(
            [
                [0, 1, 1, 1],
                [1, 1, 1, 0],
            ],
            dtype=bool,
        ),
        "Beacon": np.array(
            [
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            dtype=bool,
        ),
        "LWSS": np.array(
            [
                [0, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [0, 0, 0, 0, 1],
                [1, 0, 0, 1, 0],
            ],
            dtype=bool,
        ),
        "Gosper Gun": np.array(
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            dtype=bool,
        ),
    }
    
    
    def life_step(x):
        neighbors = sum(
            np.roll(np.roll(x, i, axis=0), j, axis=1)
            for i in (-1, 0, 1)
            for j in (-1, 0, 1)
            if i != 0 or j != 0
        )
        return (neighbors == 3) | (x & (neighbors == 2))
    
    
    def _shape():
        rows = max(8, canvas.height // cell_px.value)
        cols = max(8, canvas.width // cell_px.value)
        return rows, cols
    
    
    def _new_grid():
        rows, cols = _shape()
        rng = np.random.default_rng(seed.value)
        return rng.random((rows, cols)) < density.value
    
    
    def _frame_delay_s():
        # Higher slider value means faster simulation (shorter delay).
        fastest = speed_ms.min
        slowest = speed_ms.max
        delay_ms = fastest + slowest - speed_ms.value
        return delay_ms / 1000.0
    
    
    def draw_grid():
        grid = state["grid"]
        px = cell_px.value
    
        with hold_canvas():
            canvas.clear()
            canvas.fill_style = bg_color.value
            canvas.fill_rect(0, 0, canvas.width, canvas.height)
    
            living = np.where(grid)
            if living[0].size > 0:
                y = living[0] * px
                x = living[1] * px
                canvas.fill_style = alive_color.value
                canvas.fill_rects(x, y, px)
    
            canvas.fill_style = "#1f2b1f"
            canvas.font = "600 18px sans-serif"
            canvas.fill_text(f"Generation: {state['generation']}", 16, 28)
            canvas.font = "14px sans-serif"
            canvas.fill_text(f"Click canvas to stamp: {shape_dd.value}", 16, 48)
    
    
    def _reset_grid(*_):
        state["generation"] = 0
        state["grid"] = _new_grid()
        state["controls_dirty"] = False
        draw_grid()
    
    
    def _clear_grid(_=None):
        rows, cols = _shape()
        state["generation"] = 0
        state["grid"] = np.zeros((rows, cols), dtype=bool)
        state["controls_dirty"] = False
        draw_grid()
    
    
    def _mark_controls_dirty(*_):
        state["controls_dirty"] = True
        if not state["running"]:
            _reset_grid()
    
    
    def _ensure_current_state_from_controls():
        if state["grid"] is None or state["controls_dirty"]:
            _reset_grid()
    
    
    def _stamp_pattern(x, y):
        _ensure_current_state_from_controls()
    
        pattern = PATTERNS[shape_dd.value]
        rows, cols = state["grid"].shape
        cell_size = cell_px.value
    
        center_col = int(x // cell_size)
        center_row = int(y // cell_size)
    
        start_row = center_row - pattern.shape[0] // 2
        start_col = center_col - pattern.shape[1] // 2
    
        for pr in range(pattern.shape[0]):
            for pc in range(pattern.shape[1]):
                if not pattern[pr, pc]:
                    continue
                rr = start_row + pr
                cc = start_col + pc
                if 0 <= rr < rows and 0 <= cc < cols:
                    state["grid"][rr, cc] = True
    
        draw_grid()
    
    
    def _on_canvas_mouse_down(x, y):
        _stamp_pattern(x, y)
    
    
    async def _run_loop():
        try:
            while state["running"]:
                state["grid"] = life_step(state["grid"])
                state["generation"] += 1
                draw_grid()
                await asyncio.sleep(_frame_delay_s())
        except asyncio.CancelledError:
            pass
    
    
    def _start(_):
        _ensure_current_state_from_controls()
        if state["running"]:
            return
        state["running"] = True
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        state["task"] = loop.create_task(_run_loop())
    
    
    def _stop(_):
        state["running"] = False
        if state["task"] is not None:
            state["task"].cancel()
            state["task"] = None
    
    
    def _step(_):
        _ensure_current_state_from_controls()
        if state["running"]:
            return
        state["grid"] = life_step(state["grid"])
        state["generation"] += 1
        draw_grid()
    
    
    def _on_shape_change(change):
        if change["name"] == "value":
            draw_grid()
    
    
    start_btn.on_click(_start)
    stop_btn.on_click(_stop)
    step_btn.on_click(_step)
    random_btn.on_click(_reset_grid)
    clear_btn.on_click(_clear_grid)
    canvas.on_mouse_down(_on_canvas_mouse_down)
    shape_dd.observe(_on_shape_change, names="value")
    
    for control in [seed, cell_px, density, alive_color, bg_color]:
        control.observe(_mark_controls_dirty, names="value")
    
    _reset_grid()
    
    controls = widgets.VBox([
        widgets.HBox([seed, cell_px, density, speed_ms]),
        widgets.HBox([alive_color, bg_color, shape_dd]),
        widgets.HBox([start_btn, stop_btn, step_btn, random_btn, clear_btn]),
    ])

    return widgets.VBox([controls, canvas])