#version 100

precision mediump float;
precision mediump sampler2D;
uniform highp vec4 sk_RTAdjust;
uniform highp vec2 uAtlasSizeInv_Stage0;
attribute highp vec2 inPosition;
attribute highp vec2 inTextureCoords;
varying highp vec2 vTextureCoords_Stage0;
varying highp float vTexIndex_Stage0;
void main() {
    highp vec2 indexTexCoords = vec2(inTextureCoords.x, inTextureCoords.y);
    highp vec2 unormTexCoords = floor(0.5 * indexTexCoords);
    highp vec2 diff = indexTexCoords - 2.0 * unormTexCoords;
    highp float texIdx = 2.0 * diff.x + diff.y;
    vTextureCoords_Stage0 = unormTexCoords * uAtlasSizeInv_Stage0;
    vTexIndex_Stage0 = texIdx;
    gl_Position = vec4(inPosition.x, inPosition.y, 0.0, 1.0);
    gl_Position = vec4(gl_Position.xy * sk_RTAdjust.xz + gl_Position.ww * sk_RTAdjust.yw, 0.0, gl_Position.w);
}
