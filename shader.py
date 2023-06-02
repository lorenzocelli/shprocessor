import json
from enum import Enum
from collections import abc
from gldict import gl_type_dict
from OpenGL.GL import *
from jinja2 import Environment, FileSystemLoader


class ShaderType(Enum):

    FRAGMENT = 0,
    VERTEX = 1,
    GEOMETRY = 2

    def gl_type(self):

        if self == self.VERTEX:
            return GL_VERTEX_SHADER

        elif self == self.FRAGMENT:
            return GL_FRAGMENT_SHADER

        elif self == self.GEOMETRY:
            return GL_GEOMETRY_SHADER

    def __str__(self):

        if self == self.VERTEX:
            return "GL_VERTEX_SHADER"

        elif self == self.FRAGMENT:
            return "GL_FRAGMENT_SHADER"

        elif self == self.GEOMETRY:
            return "GL_GEOMETRY_SHADER"


class NiceNameFormat(Enum):

    CAMEL_CASE = 0,
    SNAKE_CASE = 1


class Shader:

    def __init__(self, name: str, shader_type: ShaderType, source: str):
        self.name = name
        self.type = shader_type
        self.source = source
        self.source_repr = json.dumps(source)
        self.shader_id = self.gl_init()

    def gl_init(self):
        shader_id = glCreateShader(self.type.gl_type())
        glShaderSource(shader_id, self.source)
        glCompileShader(shader_id)

        return shader_id


class Program:

    def __init__(self, name, shaders):
        self.name = name
        self.shaders = shaders
        self.compile()

    def compile(self):
        program_id = glCreateProgram()

        for shader in self.shaders:
            glAttachShader(program_id, shader.shader_id)

        glLinkProgram(program_id)

        glUseProgram(program_id)
        count = glGetProgramiv(program_id, GL_ACTIVE_UNIFORMS)

        for i in range(0, count):
            name, size, kind = glGetActiveUniform(program_id, i)
            name = name.decode('utf-8')
            print(name, size, gl_type_dict[kind])


class ShaderCollection:

    def __init__(self, path):
        self.shaderMap = {}
        self.programMap = {}
        self.shaders = []
        self.programs = []

        self.env = Environment(loader=FileSystemLoader(path), autoescape=False)



    def add(self, name: str, type: ShaderType):
        template = self.env.get_template(name)
        shader = Shader(name, type, template.render())

        self.shaderMap[name] = shader
        self.shaders.append(shader)

        return shader

    def add_program(self, name: str, shader_names: list):
        prog = Program(name, [self.shaderMap[x] for x in shader_names])

        self.programMap[name] = prog
        self.programs.append(prog)


