#version 330 core
layout (lines_adjacency) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float lineSize;

uniform vec4 viewport;

out vec4 segment;

void build_box(float lineSize, vec2 size)
{    
    vec4 prev = gl_in[0].gl_Position;
    vec4 next = gl_in[3].gl_Position;
    
    vec4 start =  gl_in[1].gl_Position;
    vec4 end =  gl_in[2].gl_Position;

    // line direction
    vec2 dir = normalize((end - start).xy * size);

    // vector normal to the line direction
    vec2 dirN = vec2(dir.y, -dir.x);

    // normal offset (line width)
    vec2 offsetN = dirN * lineSize * 2.0f / size;

    // parallel offset (lines angle)
    vec2 offsetPEnd = vec2(0.0f);
    vec2 offsetPStart = vec2(0.0f);

    // adjust parallel offset for the previous line
    if(distance(end, next) > 1e-9)
    {
        vec2 nextDir = normalize((end - next).xy * size);
        float cosine = dot(dir, nextDir);
        float sine = dot(dirN, nextDir);

        offsetPEnd = (dir * lineSize * (1/sine + cosine/sine)) * 2.0f / size;
    }

    // adjust parallel offset for the next line
    if(distance(prev, start) > 1e-9)
    {
        vec2 prevDir = normalize((prev - start).xy * size);
        float cosine = dot(dir, prevDir);
        float sine = dot(dirN, prevDir);

        offsetPStart = (dir * lineSize * (1/sine + cosine/sine)) * 2.0f / size;
    }

    vec4 offsetStart = vec4(offsetN + offsetPStart, 0, 0);
    vec4 offsetEnd = vec4(offsetN + offsetPEnd, 0, 0);

    gl_Position = start + offsetStart;
    EmitVertex ();

    gl_Position = start - offsetStart;
    EmitVertex ();

    gl_Position = end + offsetEnd;
    EmitVertex ();
    
    gl_Position = end - offsetEnd;
    EmitVertex ();
}

void main()
{
    segment = vec4(
        viewport.zw + (gl_in[1].gl_Position.xy + 1.0f) * 0.5f * viewport.xy, 
        viewport.zw + (gl_in[2].gl_Position.xy + 1.0f) * 0.5f * viewport.xy
    );

    // inflate by one pixel to allow antialiasing to transition
    float squareSize = lineSize + 1;

    build_box(squareSize / 2.0f, viewport.xy);
}