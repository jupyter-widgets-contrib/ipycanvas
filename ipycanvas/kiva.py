"""ipycanvas backend for chaco plot."""

from enable.kiva import GraphicsContextBase

from ipython.display import display

from .canvas import Canvas


def to_html_color(color):
    """Turn a list of color values from 0.0 to 1.0 into a valid HTML color."""
    scaled_color = [int(c * 255) for c in color]
    if len(scaled_color) == 4:
        return 'rgba({}, {}, {}, {})'.format(*scaled_color)
    else:
        return 'rgb({}, {}, {})'.format(*scaled_color)


class KivaGraphicsContext(GraphicsContextBase):
    """ipycanvas Canvas for Chacoplot."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)

        self.current_fill_color = [0.0, 0.0, 0.0]
        self.current_stroke_color = [0.0, 0.0, 0.0]

        self.canvas = Canvas()

        # Telling the canvas to not send any draw message before a flush call
        self.canvas.caching = True

        # display(self.canvas)

    def flush(self):
        self.canvas.flush()

    def begin_path(self):
        super().begin_path()
        self.canvas.begin_path()

    def move_to(self, x, y):
        super().move_to(x, y)
        self.canvas.move_to(x, y)

    def line_to(self, x, y):
        super().line_to(x, y)
        self.canvas.line_to(x, y)

    def rect(self, x, y, sx, sy):
        super().rect(x, y, sx, sy)
        self.canvas.rect(x, y, sx, sy)

    def close_path(self, tag=None):
        super().close_path(tag)
        self.canvas.close_path()

    def curve_to(self, x_ctrl1, y_ctrl1, x_ctrl2, y_ctrl2, x_to, y_to):
        super().curve_to(x_ctrl1, y_ctrl1, x_ctrl2, y_ctrl2, x_to, y_to)
        self.canvas.bezier_curve_to(x_ctrl1, y_ctrl1, x_ctrl2, y_ctrl2, x_to, y_to)

    def quad_curve_to(self, x_ctrl, y_ctrl, x_to, y_to):
        super().quad_curve_to(x_ctrl, y_ctrl, x_to, y_to)
        self.canvas.quadratic_curve_to(x_ctrl, y_ctrl, x_to, y_to)

    def arc(self, x, y, radius, start_angle, end_angle, cw=False):
        super().arc(x, y, radius, start_angle, end_angle, cw)
        self.canvas.quadratic_curve_to(x, y, radius, start_angle, end_angle, not cw)

    def arc_to(self, x1, y1, x2, y2, radius):
        super().arc_to(x1, y1, x2, y2, radius)
        self.canvas.arc_to(x1, y1, x2, y2, radius)

    def set_fill_color(self, color):
        super().set_fill_color(color)
        self.canvas.fill_style = to_html_color
        self.current_fill_color = color

    def get_fill_color(self):
        return self.current_fill_color

    def set_stroke_color(self, color):
        super().set_stroke_color(color)
        self.canvas.stroke_style = to_html_color
        self.current_stroke_color = color

    def get_stroke_color(self):
        return self.current_stroke_color

    def set_alpha(self, alpha):
        super().set_alpha(alpha)
        self.canvas.global_alpha = alpha

    def get_alpha(self, alpha):
        return self.canvas.global_alpha

    def set_font(self, font):
        super().set_font(font)
        self.canvas.font = '{}px {}'.format(font.size, font.face_name)

    def set_font_size(self, size):
        super().set_font_size(size)
        self.canvas.font = '{}px {}'.format(self.state.font.size, self.state.font.face_name)
