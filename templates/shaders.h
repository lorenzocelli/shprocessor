#pragma once

#include "shader.h"

namespace renderer
{
    {%- for shader in collection.shaders -%}
    {%- assign sh_name = shader.name | replace: ".", "_" -%}
    {%- assign sh_type = shader.type | append: "" -%}

    {%- assign shader_type = "vertex_shader" -%}

    {%- if sh_type == "GL_FRAGMENT_SHADER" -%}
    {%- assign shader_type = "fragment_shader" -%}
    {%- endif %}

    {%- if sh_type == "GL_GEOMETRY_SHADER" -%}
    {%- assign shader_type = "geometry_shader" -%}
    {%- endif %}

	class {{ sh_name }} : public {{ shader_type }}
	{
	public:
		{{ sh_name }}()
			: {{ shader_type }}(
				std::string({{ shader.source_repr }})
			)
		{
		}
	};
    {% endfor %}
}
