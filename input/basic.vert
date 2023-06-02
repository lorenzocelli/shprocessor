#version 330 core
layout (location = 0) in vec3 pos;

{% include 'mvp.com' %}

void main()
{
    gl_Position = projection * view * model * vec4(pos, 1.0);
}