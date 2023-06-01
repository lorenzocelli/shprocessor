#pragma once

#include "shader.h"

namespace renderer
{

	class basic_frag : public fragment_shader
	{
	public:
		basic_frag()
			: fragment_shader(
				std::string("#version 330 core\nout vec4 FragColor;\n\nuniform vec4 color;\n\nvoid main()\n{\n    FragColor = color;\n}")
			)
		{
		}
	};
    

	class basic_vert : public vertex_shader
	{
	public:
		basic_vert()
			: vertex_shader(
				std::string("#version 330 core\nlayout (location = 0) in vec3 pos;\n\nuniform mat4 model;\nuniform mat4 view;\nuniform mat4 projection;\n\nvoid main()\n{\n    gl_Position = projection * view * model * vec4(pos, 1.0);\n}")
			)
		{
		}
	};
    

	class colorful_frag : public fragment_shader
	{
	public:
		colorful_frag()
			: fragment_shader(
				std::string("#version 330 core\nout vec4 FragColor;\n\nin vec3 color;\n\nvoid main()\n{\n    FragColor = vec4(color, 1.0);\n}")
			)
		{
		}
	};
    

	class colorful_vert : public vertex_shader
	{
	public:
		colorful_vert()
			: vertex_shader(
				std::string("#version 330 core\nlayout (location = 0) in vec3 pos;\nlayout (location = 1) in vec3 col;\n\nuniform mat4 model;\nuniform mat4 view;\nuniform mat4 projection;\n\nout vec3 color;\n\nvoid main()\n{\n    gl_Position = projection * view * model * vec4(pos, 1.0);\n    color = col;\n}")
			)
		{
		}
	};
    

	class line_strip_frag : public fragment_shader
	{
	public:
		line_strip_frag()
			: fragment_shader(
				std::string("#version 330 core\nout vec4 FragColor;\n\nin vec4 segment;\n\nuniform float lineSize;\n\nuniform vec4 color;\n\nfloat segDistance(vec2 v, vec2 w, vec2 p) \n{\n    // squared distance\n    float l2 = dot(w - v, w - v); \n    \n    // segment collapsed to point\n    if (l2 == 0.0) return distance(p, v);   \n  \n    float t = dot(p - v, w - v) / l2;\n\n    if(t > 1) return distance(p, w);\n    if(t < 0) return distance(p, v);\n  \n    vec2 projection = v + t * (w - v);\n    return distance(p, projection);\n}\n\nvoid main()\n{\n    float radius = lineSize / 2;\n\n    float dist = segDistance(segment.xy, segment.zw, gl_FragCoord.xy);\n\n    FragColor = vec4(color.xyz, color.w * mix(1, 0, dist - radius + 0.5));\n}")
			)
		{
		}
	};
    

	class line_strip_geom : public geometry_shader
	{
	public:
		line_strip_geom()
			: geometry_shader(
				std::string("#version 330 core\nlayout (lines_adjacency) in;\nlayout (triangle_strip, max_vertices = 4) out;\n\nuniform mat4 model;\nuniform mat4 view;\nuniform mat4 projection;\n\nuniform float lineSize;\n\nuniform vec4 viewport;\n\nout vec4 segment;\n\nvoid build_box(float lineSize, vec2 size)\n{    \n    vec4 prev = gl_in[0].gl_Position;\n    vec4 next = gl_in[3].gl_Position;\n    \n    vec4 start =  gl_in[1].gl_Position;\n    vec4 end =  gl_in[2].gl_Position;\n\n    // line direction\n    vec2 dir = normalize((end - start).xy * size);\n\n    // vector normal to the line direction\n    vec2 dirN = vec2(dir.y, -dir.x);\n\n    // normal offset (line width)\n    vec2 offsetN = dirN * lineSize * 2.0f / size;\n\n    // parallel offset (lines angle)\n    vec2 offsetPEnd = vec2(0.0f);\n    vec2 offsetPStart = vec2(0.0f);\n\n    // adjust parallel offset for the previous line\n    if(distance(end, next) > 1e-9)\n    {\n        vec2 nextDir = normalize((end - next).xy * size);\n        float cosine = dot(dir, nextDir);\n        float sine = dot(dirN, nextDir);\n\n        offsetPEnd = (dir * lineSize * (1/sine + cosine/sine)) * 2.0f / size;\n    }\n\n    // adjust parallel offset for the next line\n    if(distance(prev, start) > 1e-9)\n    {\n        vec2 prevDir = normalize((prev - start).xy * size);\n        float cosine = dot(dir, prevDir);\n        float sine = dot(dirN, prevDir);\n\n        offsetPStart = (dir * lineSize * (1/sine + cosine/sine)) * 2.0f / size;\n    }\n\n    vec4 offsetStart = vec4(offsetN + offsetPStart, 0, 0);\n    vec4 offsetEnd = vec4(offsetN + offsetPEnd, 0, 0);\n\n    gl_Position = start + offsetStart;\n    EmitVertex ();\n\n    gl_Position = start - offsetStart;\n    EmitVertex ();\n\n    gl_Position = end + offsetEnd;\n    EmitVertex ();\n    \n    gl_Position = end - offsetEnd;\n    EmitVertex ();\n}\n\nvoid main()\n{\n    segment = vec4(\n        viewport.zw + (gl_in[1].gl_Position.xy + 1.0f) * 0.5f * viewport.xy, \n        viewport.zw + (gl_in[2].gl_Position.xy + 1.0f) * 0.5f * viewport.xy\n    );\n\n    // inflate by one pixel to allow antialiasing to transition\n    float squareSize = lineSize + 1;\n\n    build_box(squareSize / 2.0f, viewport.xy);\n}")
			)
		{
		}
	};
    

	class point_frag : public fragment_shader
	{
	public:
		point_frag()
			: fragment_shader(
				std::string("#version 330 core\nout vec4 FragColor;\n\nuniform float pointSize;\n\nin vec2 pointCenter;\n\nuniform vec4 color;\n\nvoid main()\n{\n    float radius = pointSize / 2.0f;\n\n    float a = distance(gl_FragCoord.xy, pointCenter);\n\n    FragColor = vec4(color.xyz, color.w * mix(1, 0, a - radius + 0.5));\n}")
			)
		{
		}
	};
    

	class point_geom : public geometry_shader
	{
	public:
		point_geom()
			: geometry_shader(
				std::string("#version 330 core\nlayout (points) in;\nlayout (triangle_strip, max_vertices = 4) out;\n\nuniform mat4 model;\nuniform mat4 view;\nuniform mat4 projection;\n\nuniform float pointSize;\n\nuniform vec4 viewport;\n\nout vec2 pointCenter;\n\nvoid build_point(vec4 position, vec2 vSize)\n{    \n    float hfx = vSize.x / 2.0f;\n    float hfy = vSize.y / 2.0f;\n    \n    gl_Position = position + vec4(-hfx, -hfy, 0.0, 0.0); // bottom-left\n    EmitVertex();\n    \n    gl_Position = position + vec4( hfx, -hfy, 0.0, 0.0); // bottom-right\n    EmitVertex();\n    \n    gl_Position = position + vec4(-hfx,  hfy, 0.0, 0.0); // top-left\n    EmitVertex();\n    \n    gl_Position = position + vec4( hfx,  hfy, 0.0, 0.0); // top-right\n    EmitVertex();\n    \n    EndPrimitive();\n}\n\nvoid main()\n{\n    pointCenter = viewport.zw + (gl_in[0].gl_Position.xy + 1.0f) * 0.5 * viewport.xy;\n\n    // inflate by one pixel to allow antialiasing to transition\n    float squareSize = pointSize + 1;\n\n    build_point(gl_in[0].gl_Position, 2 * squareSize/viewport.xy);\n}")
			)
		{
		}
	};
    
}
