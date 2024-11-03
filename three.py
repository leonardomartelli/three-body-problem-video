from manim import *
from functools import reduce
from math import sqrt

G = 0.5
run_time = 5
masses = [1, 6, 3]
colors = [GREEN, TEAL, ORANGE]


class ThreeBodyProblem(ThreeDScene):

    def construct(self):

        self.set_axes()
        self.set_initial_camera()
        self.add_bodies()
        self.add_trajectories()

        # self.let_play()

    def set_axes(self):
        axes = ThreeDAxes()
        axes.center()

        axes.set_stroke(width=0.5)
        self.add(axes)

    def set_initial_camera(self):

        # theta = Z-axis, gamma = X-axis, phi = Y-Axis

        self.set_camera_orientation(
            theta=-45 * DEGREES, gamma=0, phi=65 * DEGREES, zoom=0.8)

        self.begin_ambient_camera_rotation()

    def get_initial_positions(self):
        return [
            np.dot(
                2.8 * (np.random.random(3) - 0.5),
                [RIGHT, UP, OUT]
            )
            for x in range(3)
        ]

    def add_bodies(self):
        self.bodies = bodies = VGroup()
        centers = self.get_initial_positions()

        for mass, color, center in zip(masses, colors, centers):

            radius = 0.08 * np.sqrt(mass)

            body = get_sphere(radius, center=center)

            body.set_color(color)
            body.set_stroke(color, 0.1)
            body.set_opacity(0.75)
            body.mass = mass
            body.radius = radius
            body.point = center
            body.move_to(center)

            body.velocity = self.get_initial_velocity(center, centers, mass)

            bodies.add(body)

        total_mass = sum([body.mass for body in bodies])

        center_of_mass = sum(
            [body.mass * body.get_center() / total_mass for body in bodies])

        average_momentum = sum([body.mass * body.velocity / total_mass
                                for body in bodies])

        for body in bodies:
            body.shift(-center_of_mass)
            body.velocity -= average_momentum

    def get_initial_velocity(self, center, centers, mass):
        to_others = [
            center - center2
            for center2 in centers
        ]
        velocity = 0.2 * mass * normalize(np.cross(*filter(
            lambda diff: get_norm(diff) > 0,
            to_others
        )))
        return velocity

    def add_trajectories(self):
        def update_trajectory(traj, dt):
            new_point = traj.body.point
            if get_norm(new_point - traj.get_points()[-1]) > 0.01:
                traj.add_smooth_curve_to(new_point)

        for body in self.bodies:
            traj = VMobject()
            traj.body = body
            traj.start_new_path(body.point)
            traj.set_stroke(body.color, 1, opacity=0.75)
            traj.add_updater(update_trajectory)
            self.add(traj, body)

    def update_bodies(self, bodies, dt):
        num_mid_steps = 1000
        for x in range(num_mid_steps):
            for body in bodies:
                acceleration = np.zeros(3)
                for body2 in bodies:

                    if body2 is body:
                        continue

                    diff = body2.point - body.point

                    m2 = body2.mass

                    R = get_norm(diff)

                    acceleration += G * m2 * diff / (R**3)

                body.point += body.velocity * dt / num_mid_steps
                body.velocity += acceleration * dt / num_mid_steps

        for body in bodies:
            body.move_to(body.point)

        return bodies

    def let_play(self):
        bodies = self.bodies
        bodies.add_updater(self.update_bodies)
        self.add(bodies)

        for x in range(run_time):
            self.wait(frozen_frame=False)


def get_norm(v):
    return sqrt(sum(p ** 2 for p in v))


def get_sphere(radius, **kwargs):
    config = merge_dicts_recursively(
        {"radius": radius, "resolution": (24, 48)}, kwargs)
    return Sphere(**config)
