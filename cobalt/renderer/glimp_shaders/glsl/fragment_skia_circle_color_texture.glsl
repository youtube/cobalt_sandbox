#version 100

uniform highp float u_skRTHeight;
precision mediump float;
precision mediump sampler2D;
uniform mediump vec2 uDstTextureUpperLeft_Stage1;
uniform mediump vec2 uDstTextureCoordScale_Stage1;
uniform sampler2D uDstTextureSampler_Stage1;
varying highp vec4 vinCircleEdge_Stage0;
varying mediump vec4 vinColor_Stage0;
void main() {
highp     vec4 sk_FragCoord = vec4(gl_FragCoord.x, u_skRTHeight - gl_FragCoord.y, gl_FragCoord.z, gl_FragCoord.w);
    mediump vec4 outputColor_Stage0;
    mediump vec4 outputCoverage_Stage0;
    {
        highp vec4 circleEdge;
        circleEdge = vinCircleEdge_Stage0;
        outputColor_Stage0 = vinColor_Stage0;
        highp float d = length(circleEdge.xy);
        mediump float distanceToOuterEdge = circleEdge.z * (1.0 - d);
        mediump float edgeAlpha = clamp(distanceToOuterEdge, 0.0, 1.0);
        outputCoverage_Stage0 = vec4(edgeAlpha);
    }
    {
        if (all(lessThanEqual(outputCoverage_Stage0.xyz, vec3(0.0)))) {
            discard;
        }
        mediump vec2 _dstTexCoord = (sk_FragCoord.xy - uDstTextureUpperLeft_Stage1) * uDstTextureCoordScale_Stage1;
        _dstTexCoord.y = 1.0 - _dstTexCoord.y;
        mediump vec4 _dstColor = texture2D(uDstTextureSampler_Stage1, _dstTexCoord);
        gl_FragColor.w = outputColor_Stage0.w + (1.0 - outputColor_Stage0.w) * _dstColor.w;
        gl_FragColor.xyz = ((1.0 - outputColor_Stage0.w) * _dstColor.xyz + (1.0 - _dstColor.w) * outputColor_Stage0.xyz) + outputColor_Stage0.xyz * _dstColor.xyz;
        gl_FragColor = outputCoverage_Stage0 * gl_FragColor + (vec4(1.0) - outputCoverage_Stage0) * _dstColor;
    }
}
