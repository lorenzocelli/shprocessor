import json
from enum import Enum
from collections import abc

from liquid import Environment
from liquid import FileSystemLoader
from gldict import gl_type_dict

from OpenGL.GL import *


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


class Shader(abc.Mapping):

    def __init__(self, name: str, shader_type: ShaderType, source: str):
        self.name = name
        self.type = shader_type
        self.source = source
        self.source_repr = json.dumps(source)
        self.shader_id = self.gl_init()

        self._keys = ["name", "type", "source", "source_repr"]

    def gl_init(self):
        shader_id = glCreateShader(self.type.gl_type())
        glShaderSource(shader_id, self.source)
        glCompileShader(shader_id)

        return shader_id

    def __str__(self):
        return f"({self.name}, {self.type})"

    def __getitem__(self, k):
        if k in self._keys:
            return getattr(self, k)
        raise KeyError(k)

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)


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


class ShaderCollection(abc.Mapping):

    def __init__(self, path):
        self.shaderMap = {}
        self.programMap = {}

        self.env = Environment(loader=FileSystemLoader(path))

        self.shaders = []
        self.programs = []
        self._keys = [
            "shaders",
            "programs"
        ]

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

    def __getitem__(self, k):
        if k in self._keys:
            return getattr(self, k)
        raise KeyError(k)

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)


