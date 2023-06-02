#version 330 core
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

{% include 'mvp.com' %}

uniform float pointSize;

uniform vec4 viewport;

out vec2 pointCenter;

void build_point(vec4 position, vec2 vSize)
{    
    float hfx = vSize.x / 2.0f;
    float hfy = vSize.y / 2.0f;
    
    gl_Position = position + vec4(-hfx, -hfy, 0.0, 0.0); // bottom-left
    EmitVertex();
    
    gl_Position = position + vec4( hfx, -hfy, 0.0, 0.0); // bottom-right
    EmitVertex();
    
    gl_Position = position + vec4(-hfx,  hfy, 0.0, 0.0); // top-left
    EmitVertex();
    
    gl_Position = position + vec4( hfx,  hfy, 0.0, 0.0); // top-right
    EmitVertex();
    
    EndPrimitive();
}

void main()
{
    pointCenter = viewport.zw + (gl_in[0].gl_Position.xy + 1.0f) * 0.5 * viewport.xy;

    // inflate by one pixel to allow antialiasing to transition
    float squareSize = pointSize + 1;

    build_point(gl_in[0].gl_Position, 2 * squareSize/viewport.xy);
}