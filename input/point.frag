#version 330 core
out vec4 FragColor;

uniform float pointSize;

in vec2 pointCenter;

uniform vec4 color;

void main()
{
    float radius = pointSize / 2.0f;

    float a = distance(gl_FragCoord.xy, pointCenter);

    FragColor = vec4(color.xyz, color.w * mix(1, 0, a - radius + 0.5));
}