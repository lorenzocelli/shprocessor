#pragma once

#include "shader.h"

namespace renderer
{
    {%- for shader in collection.shaders %}

    {%- set name = shader.name | replace(".", "_") %}
    {%- set type = shader.type | lower | replace("gl_", "") %}

	class {{ name }} : public {{ type }}
	{
	public:
		{{ name }}()
			: {{ type }}(
				std::string({{ shader.source_repr }})
			)
		{
		}
	};
    {% endfor %}
}
