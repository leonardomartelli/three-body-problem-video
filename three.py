from manim import *

from math import sqrt

N_SYSTEMS = 1
G = 0.5
run_time = 55
masses = [6, 1, 3]

colors = [RED, GREEN, PURPLE]


def get_norm(v):
    return sqrt(sum(p ** 2 for p in v))


def get_sphere(radius, **kwargs):
    config = merge_dicts_recursively(
        {"radius": radius, "resolution": (24, 48)}, kwargs)
    return Sphere(**config)


class ThreeBodyProblem(ThreeDScene):

    def construct(self):
        self.set_axes()
        self.set_camera()

        self.add_bodies()
        self.add_trajectories()

        self.let_play()

    def set_axes(self):
        axes = ThreeDAxes()
        axes.center()

        axes.set_stroke(width=0.5)
        axes.set_color(LIGHT_GRAY)
        self.add(axes)

    def set_camera(self):

        # theta = Z-axis, gamma = X-axis, phi = Y-Axis

        self.set_camera_orientation(
            theta=-45 * DEGREES, gamma=0, phi=65 * DEGREES, zoom=0.8)

        self.begin_ambient_camera_rotation(0.05)
        self.begin_ambient_camera_rotation(0.02, 'gamma')

    def get_initial_positions(self):
        return [
            np.array([-0.8886498, -1.34690256, -1.10335772]),
            np.array([1.30319651,  0.94171346, -0.89115685]),
            np.array([1.48236905, 0.63810833, 0.97979033])
        ]

    def add_bodies(self):
        self.bodies = bodies = VGroup()

        centers = self.get_initial_positions()

        for mass, color, center in zip(masses, colors, centers):

            radius = 0.08 * np.sqrt(mass)

            body = get_sphere(radius, center=center)

            body.set_color(color)
            body.set_stroke(color, 0.1)
            body.set_opacity(1)
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
        velocity = 0.08 * mass * normalize(np.cross(*filter(
            lambda diff: get_norm(diff) > 0,
            to_others
        )))
        return velocity

    def add_trajectories(self):
        def update_trajectory(traj: VMobject, dt):
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
            for body_i in bodies:
                acceleration = np.zeros(3)
                for body_j in bodies:

                    if body_j is body_i:
                        continue

                    diff = body_j.point - body_i.point

                    m2 = body_j.mass

                    R = get_norm(diff)

                    acceleration += G * m2 * diff / (R**3)

                body_i.point += body_i.velocity * dt / num_mid_steps
                body_i.velocity += acceleration * dt / num_mid_steps

        for body_i in bodies:
            body_i.move_to(body_i.point)

        return bodies

    def let_play(self):
        self.bodies.add_updater(self.update_bodies)
        self.add(self.bodies)

        for x in range(run_time):
            self.wait(frozen_frame=False)
