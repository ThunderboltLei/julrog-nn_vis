from OpenGL.GL import *

from models.grid import Grid
from opengl_helper.render_utility import VertexDataHandler, RenderSet, render_setting_0, render_setting_1
from opengl_helper.shader import RenderShaderHandler, RenderShader
from processing.edge_processing import EdgeProcessor
from utility.performance import track_time
from utility.window import Window


class EdgeRenderer:
    def __init__(self, edge_processor: EdgeProcessor, grid: Grid):
        self.edge_processor = edge_processor
        self.grid = grid

        shader_handler: RenderShaderHandler = RenderShaderHandler()
        sample_point_shader: RenderShader = shader_handler.create("sample_point", "sample/sample.vert",
                                                                  "basic/discard_screen_color.frag")
        sample_sphere_shader: RenderShader = shader_handler.create("sample_sphere", "sample/sample_impostor.vert",
                                                                   "sample/point_to_sphere_impostor_phong.frag",
                                                                   "sample/point_to_sphere_impostor.geom")
        sample_transparent_shader: RenderShader = shader_handler.create("sample_transparent_sphere",
                                                                        "sample/sample_impostor.vert",
                                                                        "sample/point_to_sphere_impostor_transparent.frag",
                                                                        "sample/point_to_sphere_impostor.geom")
        sample_ellipse_shader: RenderShader = shader_handler.create("sample_ellipsoid_transparent",
                                                                    "sample/sample_impostor.vert",
                                                                    "sample/line_to_ellipsoid_impostor_transparent.frag",
                                                                    "sample/line_to_ellipsoid_impostor.geom")

        self.data_handler: VertexDataHandler = VertexDataHandler([(self.edge_processor.sample_buffer, 0)])

        self.point_render: RenderSet = RenderSet(sample_point_shader, self.data_handler)
        self.sphere_render: RenderSet = RenderSet(sample_sphere_shader, self.data_handler)
        self.transparent_render: RenderSet = RenderSet(sample_transparent_shader, self.data_handler)
        self.ellipse_render: RenderSet = RenderSet(sample_ellipse_shader, self.data_handler)

    @track_time
    def render_point(self, window: Window, clear: bool = True, swap: bool = False):
        sampled_points: int = self.edge_processor.get_buffer_points()

        self.point_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                            ("view", window.cam.view, "mat4"),
                                            ("screen_width", 1920.0, "float"),
                                            ("screen_height", 1080.0, "float")])

        self.point_render.set()

        render_setting_0(clear)
        glPointSize(10.0)
        glDrawArrays(GL_POINTS, 0, sampled_points)
        if swap:
            window.swap()

    @track_time
    def render_line(self, window: Window, clear: bool = True, swap: bool = False):
        sampled_points: int = self.edge_processor.get_buffer_points()

        self.point_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                            ("view", window.cam.view, "mat4"),
                                            ("screen_width", 1920.0, "float"),
                                            ("screen_height", 1080.0, "float")])

        self.point_render.set()

        render_setting_0(clear)
        glLineWidth(2.0)
        glDrawArrays(GL_LINE_STRIP, 0, sampled_points)
        if swap:
            window.swap()

    @track_time
    def render_sphere(self, window: Window, sphere_radius: float = 0.05, clear: bool = True, swap: bool = False):
        sampled_points: int = self.edge_processor.get_buffer_points()

        self.sphere_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                             ("view", window.cam.view, "mat4"),
                                             ("sphere_radius", sphere_radius, "float")])

        self.sphere_render.set()

        render_setting_0(clear)
        glDrawArrays(GL_POINTS, 0, sampled_points)
        if swap:
            window.swap()

    @track_time
    def render_transparent_sphere(self, window: Window, sphere_radius: float = 0.05, clear: bool = True,
                                  swap: bool = False):
        sampled_points: int = self.edge_processor.get_buffer_points()

        near, far = self.grid.get_near_far_from_view(window.cam.view)
        self.transparent_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                                  ("view", window.cam.view, "mat4"),
                                                  ("farthest_point_view_z", far, "float"),
                                                  ("nearest_point_view_z", near, "float"),
                                                  ("sphere_radius", sphere_radius, "float")])

        self.transparent_render.set()

        render_setting_1(clear)
        glDrawArrays(GL_POINTS, 0, sampled_points)
        if swap:
            window.swap()

    @track_time
    def render_ellipsoid_transparent(self, window: Window, radius: float = 0.05, clear: bool = True, swap: bool = False):
        sampled_points: int = self.edge_processor.get_buffer_points()

        near, far = self.grid.get_near_far_from_view(window.cam.view)
        self.ellipse_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                              ("view", window.cam.view, "mat4"),
                                              ("farthest_point_view_z", far, "float"),
                                              ("nearest_point_view_z", near, "float"),
                                              ("sample_radius", self.edge_processor.sample_length * 0.5, "float")])

        self.ellipse_render.set()

        render_setting_1(clear)
        glDrawArrays(GL_LINE_STRIP, 0, sampled_points)
        if swap:
            window.swap()

    def delete(self):
        self.data_handler.delete()
