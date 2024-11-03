from manim import *


class CreateCircle(ThreeDScene):
    def construct(self):

        self.set_axes()
        self.set_initial_camera()

        circle = Circle(radius=0.1)
        circle.set_color(RED)
        circle.set_fill(RED, opacity=1)

        pos0 = (1, 2, 0)

        circle.move_to(pos0)

        def update(circle: Circle):
            pos = (circle.point_at_angle(0) + 1) % 2

            circle.move_to(pos)

        circle.add_updater(update)

        self.play(FadeIn(circle), run_time=10)

    def set_axes(self):
        axes = ThreeDAxes()
        axes.center()

        labels = axes.get_axis_labels(
            Text(
                "x-axis").scale(0.7), Text("y-axis").scale(0.45), Text("z-axis").scale(0.45)
        )
        self.add(axes, labels)

        self.add(axes)

    def set_initial_camera(self):

        # theta = Z-axis, gamma = X-axis, phi = Y-Axis

        self.set_camera_orientation(
            theta=-45 * DEGREES, gamma=0, phi=65 * DEGREES, zoom=1.1)
