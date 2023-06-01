#version 330 core
out vec4 FragColor;

in vec4 segment;

uniform float lineSize;

uniform vec4 color;

float segDistance(vec2 v, vec2 w, vec2 p) 
{
    // squared distance
    float l2 = dot(w - v, w - v); 
    
    // segment collapsed to point
    if (l2 == 0.0) return distance(p, v);   
  
    float t = dot(p - v, w - v) / l2;

    if(t > 1) return distance(p, w);
    if(t < 0) return distance(p, v);
  
    vec2 projection = v + t * (w - v);
    return distance(p, projection);
}

void main()
{
    float radius = lineSize / 2;

    float dist = segDistance(segment.xy, segment.zw, gl_FragCoord.xy);

    FragColor = vec4(color.xyz, color.w * mix(1, 0, dist - radius + 0.5));
}