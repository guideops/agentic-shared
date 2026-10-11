/* dsx-metal-text | metal-fx 2.0.11 (MIT, Jakub Antalik) incl. Paper Shaders liquidMetal (Apache-2.0, Paper Design). Needs dsx-metal.js loaded first. */
(()=>{var Xn=Object.create;var uo=Object.defineProperty;var Yn=Object.getOwnPropertyDescriptor;var qn=Object.getOwnPropertyNames;var jn=Object.getPrototypeOf,Qn=Object.prototype.hasOwnProperty;var Jn=(e,t)=>()=>(t||e((t={exports:{}}).exports,t),t.exports);var Kn=(e,t,n,a)=>{if(t&&typeof t=="object"||typeof t=="function")for(let o of qn(t))!Qn.call(e,o)&&o!==n&&uo(e,o,{get:()=>t[o],enumerable:!(a=Yn(t,o))||a.enumerable});return e};var Zn=(e,t,n)=>(n=e!=null?Xn(jn(e)):{},Kn(t||!e||!e.__esModule?uo(n,"default",{value:e,enumerable:!0}):n,e));var po=Jn((wi,fo)=>{fo.exports=window.React});var ho=window.React,xi=ho.Fragment;function ge(e,t,n){return ho.createElement(e,n==null?t:{...t,key:n})}var mo=ge;var z=Zn(po(),1);function go(e){let t=e.replace("#","");(t.length===3||t.length===4)&&(t=t.split("").map(a=>a+a).join(""));let n=t.length>=8?parseInt(t.slice(6,8),16)/255:1;return[parseInt(t.slice(0,2),16)/255,parseInt(t.slice(2,4),16)/255,parseInt(t.slice(4,6),16)/255,n]}function on(e,t,n){e/=255,t/=255,n/=255;let a=Math.max(e,t,n),o=Math.min(e,t,n),i=a-o,r=0,l=a===0?0:i/a;return i!==0&&(a===e?r=((t-n)/i+6)%6:a===t?r=(n-e)/i+2:r=(e-t)/i+4,r/=6),[r,l,a]}function nn(e,t,n){let a=Math.floor(e*6),o=e*6-a,i=n*(1-t),r=n*(1-o*t),l=n*(1-(1-o)*t),s=0,c=0,u=0;switch(a%6){case 0:s=n,c=l,u=i;break;case 1:s=r,c=n,u=i;break;case 2:s=i,c=n,u=l;break;case 3:s=i,c=r,u=n;break;case 4:s=l,c=i,u=n;break;case 5:s=n,c=i,u=r;break}return[Math.round(s*255),Math.round(c*255),Math.round(u*255)]}var ea=66,ta=66,oa=1500,na=1,xo=16,aa=96,ra=2,ia=0;var sa=1;var We={colorBack:"#00000000",speed:1,repetition:1.5,softness:.05,shiftRed:.3,shiftBlue:.3,distortion:.1,contour:.4,angle:90,shape:ia,scale:1,rotation:0,offsetX:0,offsetY:0,originX:.5,originY:.5,worldWidth:0,worldHeight:0,fit:sa},la={name:"chromatic",modes:{dark:{...We,colorTint:"#88ccff2e",shiftRed:.75,shiftBlue:.75,repetition:2,softness:.09,shaderOpacity:1},light:{...We,colorTint:"#66b0ff99",shiftRed:.6,shiftBlue:.6,shaderOpacity:1}}},ca={name:"silver",modes:{dark:{...We,colorTint:"#ffffff66",shaderOpacity:.88},light:{...We,colorTint:"#ffffff40",shaderOpacity:1}}},ua={name:"gold",modes:{dark:{...We,colorTint:"#ffcc55cc",speed:.85,shaderOpacity:.92},light:{...We,colorTint:"#f7d488aa",shaderOpacity:1}}},Ct={chromatic:la,silver:ca,gold:ua},da=`
#define TWO_PI 6.28318530718
#define PI 3.14159265358979323846
`,ha=`
vec2 rotate(vec2 uv, float th) {
  return mat2(cos(th), sin(th), -sin(th), cos(th)) * uv;
}
`,ma=`
  color += 1. / 256. * (fract(sin(dot(.014 * gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453123) - .5);
`,fa=`
vec3 permute(vec3 x) { return mod(((x * 34.0) + 1.0) * x, 289.0); }
float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
    -0.577350269189626, 0.024390243902439);
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1;
  i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0))
    + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy),
      dot(x12.zw, x12.zw)), 0.0);
  m = m * m;
  m = m * m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
  vec3 g;
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
`,pa=`#version 300 es
precision mediump float;

uniform sampler2D u_image;
uniform float u_imageAspectRatio;

uniform vec2 u_resolution;
uniform float u_time;

uniform vec4 u_colorBack;
uniform vec4 u_colorTint;

uniform float u_softness;
uniform float u_repetition;
uniform float u_shiftRed;
uniform float u_shiftBlue;
uniform float u_distortion;
uniform float u_contour;
uniform float u_angle;

uniform float u_shape;
uniform bool u_isImage;

in vec2 v_objectUV;
in vec2 v_responsiveUV;
in vec2 v_responsiveBoxGivenSize;
in vec2 v_imageUV;

out vec4 fragColor;

${da}
${ha}
${fa}

float getColorChanges(float c1, float c2, float stripe_p, vec3 w, float blur, float bump, float tint) {

  float ch = mix(c2, c1, smoothstep(.0, 2. * blur, stripe_p));

  float border = w[0];
  ch = mix(ch, c2, smoothstep(border, border + 2. * blur, stripe_p));

  if (u_isImage == true) {
    bump = smoothstep(.2, .8, bump);
  }
  border = w[0] + .4 * (1. - bump) * w[1];
  ch = mix(ch, c1, smoothstep(border, border + 2. * blur, stripe_p));

  border = w[0] + .5 * (1. - bump) * w[1];
  ch = mix(ch, c2, smoothstep(border, border + 2. * blur, stripe_p));

  border = w[0] + w[1];
  ch = mix(ch, c1, smoothstep(border, border + 2. * blur, stripe_p));

  float gradient_t = (stripe_p - w[0] - w[1]) / w[2];
  float gradient = mix(c1, c2, smoothstep(0., 1., gradient_t));
  ch = mix(ch, gradient, smoothstep(border, border + .5 * blur, stripe_p));

  // Tint color is applied with color burn blending
  ch = mix(ch, 1. - min(1., (1. - ch) / max(tint, 0.0001)), u_colorTint.a);
  return ch;
}

float getImgFrame(vec2 uv, float th) {
  float frame = 1.;
  frame *= smoothstep(0., th, uv.y);
  frame *= 1.0 - smoothstep(1. - th, 1., uv.y);
  frame *= smoothstep(0., th, uv.x);
  frame *= 1.0 - smoothstep(1. - th, 1., uv.x);
  return frame;
}

float blurEdge3x3(sampler2D tex, vec2 uv, vec2 dudx, vec2 dudy, float radius, float centerSample) {
  vec2 texel = 1.0 / vec2(textureSize(tex, 0));
  vec2 r = radius * texel;

  float w1 = 1.0, w2 = 2.0, w4 = 4.0;
  float norm = 16.0;
  float sum = w4 * centerSample;

  sum += w2 * textureGrad(tex, uv + vec2(0.0, -r.y), dudx, dudy).r;
  sum += w2 * textureGrad(tex, uv + vec2(0.0, r.y), dudx, dudy).r;
  sum += w2 * textureGrad(tex, uv + vec2(-r.x, 0.0), dudx, dudy).r;
  sum += w2 * textureGrad(tex, uv + vec2(r.x, 0.0), dudx, dudy).r;

  sum += w1 * textureGrad(tex, uv + vec2(-r.x, -r.y), dudx, dudy).r;
  sum += w1 * textureGrad(tex, uv + vec2(r.x, -r.y), dudx, dudy).r;
  sum += w1 * textureGrad(tex, uv + vec2(-r.x, r.y), dudx, dudy).r;
  sum += w1 * textureGrad(tex, uv + vec2(r.x, r.y), dudx, dudy).r;

  return sum / norm;
}

float lst(float edge0, float edge1, float x) {
  return clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
}

void main() {

  const float firstFrameOffset = 2.8;
  float t = .3 * (u_time + firstFrameOffset);

  vec2 uv = v_imageUV;
  vec2 dudx = dFdx(v_imageUV);
  vec2 dudy = dFdy(v_imageUV);
  vec4 img = textureGrad(u_image, uv, dudx, dudy);

  if (u_isImage == false) {
    uv = v_objectUV + .5;
    uv.y = 1. - uv.y;
  }

  float cycleWidth = u_repetition;
  float edge = 0.;
  float contOffset = 1.;

  vec2 rotatedUV = uv - vec2(.5);
  float angle = (-u_angle + 70.) * PI / 180.;
  float cosA = cos(angle);
  float sinA = sin(angle);
  rotatedUV = vec2(
  rotatedUV.x * cosA - rotatedUV.y * sinA,
  rotatedUV.x * sinA + rotatedUV.y * cosA
  ) + vec2(.5);

  if (u_isImage == true) {
    float edgeRaw = img.r;
    edge = blurEdge3x3(u_image, uv, dudx, dudy, 6., edgeRaw);
    edge = pow(edge, 1.6);
    edge *= mix(0.0, 1.0, smoothstep(0.0, 0.4, u_contour));
  } else {
    if (u_shape < 1.) {
      // full-fill on canvas
      vec2 borderUV = v_responsiveUV + .5;
      float ratio = v_responsiveBoxGivenSize.x / v_responsiveBoxGivenSize.y;
      vec2 mask = min(borderUV, 1. - borderUV);
      vec2 pixel_thickness = min(250. / v_responsiveBoxGivenSize, vec2(.5));
      float maskX = smoothstep(0.0, pixel_thickness.x, mask.x);
      float maskY = smoothstep(0.0, pixel_thickness.y, mask.y);
      maskX = pow(maskX, .25);
      maskY = pow(maskY, .25);
      edge = clamp(1. - maskX * maskY, 0., 1.);

      uv = v_responsiveUV;
      if (ratio > 1.) {
        uv.y /= ratio;
      } else {
        uv.x *= ratio;
      }
      uv += .5;
      uv.y = 1. - uv.y;

      cycleWidth *= 2.;
      contOffset = 1.5;

    } else if (u_shape < 2.) {
      // circle
      vec2 shapeUV = uv - .5;
      shapeUV *= .67;
      edge = pow(clamp(3. * length(shapeUV), 0., 1.), 18.);
    } else if (u_shape < 3.) {
      // daisy
      vec2 shapeUV = uv - .5;
      shapeUV *= 1.68;

      float r = length(shapeUV) * 2.;
      float a = atan(shapeUV.y, shapeUV.x) + .2;
      r *= (1. + .05 * sin(3. * a + 2. * t));
      float f = abs(cos(a * 3.));
      edge = smoothstep(f, f + .7, r);
      edge *= edge;

      uv *= .8;
      cycleWidth *= 1.6;

    } else if (u_shape < 4.) {
      // diamond
      vec2 shapeUV = uv - .5;
      shapeUV = rotate(shapeUV, .25 * PI);
      shapeUV *= 1.42;
      shapeUV += .5;
      vec2 mask = min(shapeUV, 1. - shapeUV);
      vec2 pixel_thickness = vec2(.15);
      float maskX = smoothstep(0.0, pixel_thickness.x, mask.x);
      float maskY = smoothstep(0.0, pixel_thickness.y, mask.y);
      maskX = pow(maskX, .25);
      maskY = pow(maskY, .25);
      edge = clamp(1. - maskX * maskY, 0., 1.);
    } else if (u_shape < 5.) {
      // metaballs
      vec2 shapeUV = uv - .5;
      shapeUV *= 1.3;
      edge = 0.;
      for (int i = 0; i < 5; i++) {
        float fi = float(i);
        float speed = 1.5 + 2./3. * sin(fi * 12.345);
        float angle = -fi * 1.5;
        vec2 dir1 = vec2(cos(angle), sin(angle));
        vec2 dir2 = vec2(cos(angle + 1.57), sin(angle + 1.));
        vec2 traj = .4 * (dir1 * sin(t * speed + fi * 1.23) + dir2 * cos(t * (speed * 0.7) + fi * 2.17));
        float d = length(shapeUV + traj);
        edge += pow(1.0 - clamp(d, 0.0, 1.0), 4.0);
      }
      edge = 1. - smoothstep(.65, .9, edge);
      edge = pow(edge, 4.);
    }

    edge = mix(smoothstep(.9 - 2. * fwidth(edge), .9, edge), edge, smoothstep(0.0, 0.4, u_contour));

  }

  float opacity = 0.;
  if (u_isImage == true) {
    opacity = img.g;
    float frame = getImgFrame(v_imageUV, 0.);
    opacity *= frame;
  } else {
    opacity = 1. - smoothstep(.9 - 2. * fwidth(edge), .9, edge);
    if (u_shape < 2.) {
      edge = 1.2 * edge;
    } else if (u_shape < 5.) {
      edge = 1.8 * pow(edge, 1.5);
    }
  }

  float diagBLtoTR = rotatedUV.x - rotatedUV.y;
  float diagTLtoBR = rotatedUV.x + rotatedUV.y;

  vec3 color = vec3(0.);
  vec3 color1 = vec3(.98, 0.98, 1.);
  vec3 color2 = vec3(.1, .1, .1 + .1 * smoothstep(.7, 1.3, diagTLtoBR));

  vec2 grad_uv = uv - .5;

  float dist = length(grad_uv + vec2(0., .2 * diagBLtoTR));
  grad_uv = rotate(grad_uv, (.25 - .2 * diagBLtoTR) * PI);
  float direction = grad_uv.x;

  float bump = pow(1.8 * dist, 1.2);
  bump = 1. - bump;
  bump *= pow(uv.y, .3);


  float thin_strip_1_ratio = .12 / cycleWidth * (1. - .4 * bump);
  float thin_strip_2_ratio = .07 / cycleWidth * (1. + .4 * bump);
  float wide_strip_ratio = (1. - thin_strip_1_ratio - thin_strip_2_ratio);

  float thin_strip_1_width = cycleWidth * thin_strip_1_ratio;
  float thin_strip_2_width = cycleWidth * thin_strip_2_ratio;

  float noise = snoise(uv - t);

  edge += (1. - edge) * u_distortion * noise;

  direction += diagBLtoTR;
  float contour = 0.;
  direction -= 2. * noise * diagBLtoTR * (smoothstep(0., 1., edge) * (1.0 - smoothstep(0., 1., edge)));
  direction *= mix(1., 1. - edge, smoothstep(.5, 1., u_contour));
  direction -= 1.7 * edge * smoothstep(.5, 1., u_contour);
  direction += .2 * pow(u_contour, 4.) * (1.0 - smoothstep(0., 1., edge));

  bump *= clamp(pow(uv.y, .1), .3, 1.);
  direction *= (.1 + (1.1 - edge) * bump);

  direction *= (.4 + .6 * (1.0 - smoothstep(.5, 1., edge)));
  direction += .18 * (smoothstep(.1, .2, uv.y) * (1.0 - smoothstep(.2, .4, uv.y)));
  direction += .03 * (smoothstep(.1, .2, 1. - uv.y) * (1.0 - smoothstep(.2, .4, 1. - uv.y)));

  direction *= (.5 + .5 * pow(uv.y, 2.));
  direction *= cycleWidth;
  direction -= t;


  float colorDispersion = (1. - bump);
  colorDispersion = clamp(colorDispersion, 0., 1.);
  float dispersionRed = colorDispersion;
  dispersionRed += .03 * bump * noise;
  dispersionRed += 5. * (smoothstep(-.1, .2, uv.y) * (1.0 - smoothstep(.1, .5, uv.y))) * (smoothstep(.4, .6, bump) * (1.0 - smoothstep(.4, 1., bump)));
  dispersionRed -= diagBLtoTR;

  float dispersionBlue = colorDispersion;
  dispersionBlue *= 1.3;
  dispersionBlue += (smoothstep(0., .4, uv.y) * (1.0 - smoothstep(.1, .8, uv.y))) * (smoothstep(.4, .6, bump) * (1.0 - smoothstep(.4, .8, bump)));
  dispersionBlue -= .2 * edge;

  dispersionRed *= (u_shiftRed / 20.);
  dispersionBlue *= (u_shiftBlue / 20.);

  float blur = 0.;
  float rExtraBlur = 0.;
  float gExtraBlur = 0.;
  if (u_isImage == true) {
    float softness = 0.05 * u_softness;
    blur = softness + .5 * smoothstep(1., 10., u_repetition) * smoothstep(.0, 1., edge);
    float smallCanvasT = 1.0 - smoothstep(100., 500., min(u_resolution.x, u_resolution.y));
    blur += smallCanvasT * smoothstep(.0, 1., edge);
    rExtraBlur = softness * (0.05 + .1 * (u_shiftRed / 20.) * bump);
    gExtraBlur = softness * 0.05 / max(0.001, abs(1. - diagBLtoTR));
  } else {
    blur = u_softness / 15. + .3 * contour;
  }

  vec3 w = vec3(thin_strip_1_width, thin_strip_2_width, wide_strip_ratio);
  w[1] -= .02 * smoothstep(.0, 1., edge + bump);
  float stripe_r = fract(direction + dispersionRed);
  float r = getColorChanges(color1.r, color2.r, stripe_r, w, blur + fwidth(stripe_r) + rExtraBlur, bump, u_colorTint.r);
  float stripe_g = fract(direction);
  float g = getColorChanges(color1.g, color2.g, stripe_g, w, blur + fwidth(stripe_g) + gExtraBlur, bump, u_colorTint.g);
  float stripe_b = fract(direction - dispersionBlue);
  float b = getColorChanges(color1.b, color2.b, stripe_b, w, blur + fwidth(stripe_b), bump, u_colorTint.b);

  color = vec3(r, g, b);
  color *= opacity;

  vec3 bgColor = u_colorBack.rgb * u_colorBack.a;
  color = color + bgColor * (1. - opacity);
  opacity = opacity + u_colorBack.a * (1. - opacity);

  ${ma}

  fragColor = vec4(color, opacity);
}
`,ga=`#version 300 es
precision mediump float;

layout(location = 0) in vec4 a_position;

uniform vec2 u_resolution;
uniform float u_pixelRatio;
uniform float u_imageAspectRatio;
uniform float u_originX;
uniform float u_originY;
uniform float u_worldWidth;
uniform float u_worldHeight;
uniform float u_fit;
uniform float u_scale;
uniform float u_rotation;
uniform float u_offsetX;
uniform float u_offsetY;

out vec2 v_objectUV;
out vec2 v_objectBoxSize;
out vec2 v_responsiveUV;
out vec2 v_responsiveBoxGivenSize;
out vec2 v_patternUV;
out vec2 v_patternBoxSize;
out vec2 v_imageUV;

vec3 getBoxSize(float boxRatio, vec2 givenBoxSize) {
  vec2 box = vec2(0.);
  // fit = none
  box.x = boxRatio * min(givenBoxSize.x / boxRatio, givenBoxSize.y);
  float noFitBoxWidth = box.x;
  if (u_fit == 1.) { // fit = contain
    box.x = boxRatio * min(u_resolution.x / boxRatio, u_resolution.y);
  } else if (u_fit == 2.) { // fit = cover
    box.x = boxRatio * max(u_resolution.x / boxRatio, u_resolution.y);
  }
  box.y = box.x / boxRatio;
  return vec3(box, noFitBoxWidth);
}

void main() {
  gl_Position = a_position;

  vec2 uv = gl_Position.xy * .5;
  vec2 boxOrigin = vec2(.5 - u_originX, u_originY - .5);
  vec2 givenBoxSize = vec2(u_worldWidth, u_worldHeight);
  givenBoxSize = max(givenBoxSize, vec2(1.)) * u_pixelRatio;
  float r = u_rotation * 3.14159265358979323846 / 180.;
  mat2 graphicRotation = mat2(cos(r), sin(r), -sin(r), cos(r));
  vec2 graphicOffset = vec2(-u_offsetX, u_offsetY);


  // ===================================================

  float fixedRatio = 1.;
  vec2 fixedRatioBoxGivenSize = vec2(
  (u_worldWidth == 0.) ? u_resolution.x : givenBoxSize.x,
  (u_worldHeight == 0.) ? u_resolution.y : givenBoxSize.y
  );

  v_objectBoxSize = getBoxSize(fixedRatio, fixedRatioBoxGivenSize).xy;
  vec2 objectWorldScale = u_resolution.xy / v_objectBoxSize;

  v_objectUV = uv;
  v_objectUV *= objectWorldScale;
  v_objectUV += boxOrigin * (objectWorldScale - 1.);
  v_objectUV += graphicOffset;
  v_objectUV /= u_scale;
  v_objectUV = graphicRotation * v_objectUV;

  // ===================================================

  v_responsiveBoxGivenSize = vec2(
  (u_worldWidth == 0.) ? u_resolution.x : givenBoxSize.x,
  (u_worldHeight == 0.) ? u_resolution.y : givenBoxSize.y
  );
  float responsiveRatio = v_responsiveBoxGivenSize.x / v_responsiveBoxGivenSize.y;
  vec2 responsiveBoxSize = getBoxSize(responsiveRatio, v_responsiveBoxGivenSize).xy;
  vec2 responsiveBoxScale = u_resolution.xy / responsiveBoxSize;

  v_responsiveUV = uv;
  v_responsiveUV *= responsiveBoxScale;
  v_responsiveUV += boxOrigin * (responsiveBoxScale - 1.);
  v_responsiveUV += graphicOffset;
  v_responsiveUV /= u_scale;
  v_responsiveUV.x *= responsiveRatio;
  v_responsiveUV = graphicRotation * v_responsiveUV;
  v_responsiveUV.x /= responsiveRatio;

  // ===================================================

  float patternBoxRatio = givenBoxSize.x / givenBoxSize.y;
  vec2 patternBoxGivenSize = vec2(
  (u_worldWidth == 0.) ? u_resolution.x : givenBoxSize.x,
  (u_worldHeight == 0.) ? u_resolution.y : givenBoxSize.y
  );
  patternBoxRatio = patternBoxGivenSize.x / patternBoxGivenSize.y;

  vec3 boxSizeData = getBoxSize(patternBoxRatio, patternBoxGivenSize);
  v_patternBoxSize = boxSizeData.xy;
  float patternBoxNoFitBoxWidth = boxSizeData.z;
  vec2 patternBoxScale = u_resolution.xy / v_patternBoxSize;

  v_patternUV = uv;
  v_patternUV += graphicOffset / patternBoxScale;
  v_patternUV += boxOrigin;
  v_patternUV -= boxOrigin / patternBoxScale;
  v_patternUV *= u_resolution.xy;
  v_patternUV /= u_pixelRatio;
  if (u_fit > 0.) {
    v_patternUV *= (patternBoxNoFitBoxWidth / v_patternBoxSize.x);
  }
  v_patternUV /= u_scale;
  v_patternUV = graphicRotation * v_patternUV;
  v_patternUV += boxOrigin / patternBoxScale;
  v_patternUV -= boxOrigin;
  // x100 is a default multiplier between vertex and fragmant shaders
  // we use it to avoid UV presision issues
  v_patternUV *= .01;

  // ===================================================

  vec2 imageBoxSize;
  if (u_fit == 1.) { // contain
    imageBoxSize.x = min(u_resolution.x / u_imageAspectRatio, u_resolution.y) * u_imageAspectRatio;
  } else if (u_fit == 2.) { // cover
    imageBoxSize.x = max(u_resolution.x / u_imageAspectRatio, u_resolution.y) * u_imageAspectRatio;
  } else {
    imageBoxSize.x = min(10.0, 10.0 / u_imageAspectRatio * u_imageAspectRatio);
  }
  imageBoxSize.y = imageBoxSize.x / u_imageAspectRatio;
  vec2 imageBoxScale = u_resolution.xy / imageBoxSize;

  v_imageUV = uv;
  v_imageUV *= imageBoxScale;
  v_imageUV += boxOrigin * (imageBoxScale - 1.);
  v_imageUV += graphicOffset;
  v_imageUV /= u_scale;
  v_imageUV.x *= u_imageAspectRatio;
  v_imageUV = graphicRotation * v_imageUV;
  v_imageUV.x /= u_imageAspectRatio;

  v_imageUV += .5;
  v_imageUV.y = 1. - v_imageUV.y;
}`,xa=pa;function vo(e,t,n){let a=e.createShader(t);if(!a)throw new Error("metal-fx: gl.createShader returned null");if(e.shaderSource(a,n),e.compileShader(a),!e.getShaderParameter(a,e.COMPILE_STATUS)){let o=e.getShaderInfoLog(a);throw e.deleteShader(a),new Error(`metal-fx: shader compile failed: ${o??"(no info log)"}`)}return a}function va(e,t,n){let a=e.createProgram();if(!a)throw new Error("metal-fx: gl.createProgram returned null");if(e.attachShader(a,t),e.attachShader(a,n),e.linkProgram(a),!e.getProgramParameter(a,e.LINK_STATUS)){let o=e.getProgramInfoLog(a);throw e.deleteProgram(a),new Error(`metal-fx: program link failed: ${o??"(no info log)"}`)}return a}var an=140,rn=40,sn=1.6,ln=1.3,x=null,Le=null;function Rt(){var e;if(Le!==null)return Le;if(typeof document>"u")return Le=!1;try{let t=document.createElement("canvas").getContext("webgl2");Le=!!t,(e=t?.getExtension("WEBGL_lose_context"))==null||e.loseContext()}catch{Le=!1}return Le}var Vt=null;function wa(e){Vt=e}var ba=["u_resolution","u_time","u_pixelRatio","u_colorBack","u_colorTint","u_repetition","u_softness","u_shiftRed","u_shiftBlue","u_distortion","u_contour","u_angle","u_shape","u_isImage","u_image","u_originX","u_originY","u_worldWidth","u_worldHeight","u_fit","u_scale","u_rotation","u_offsetX","u_offsetY","u_imageAspectRatio"];function wo(e){e.enable(e.BLEND),e.blendFunc(e.ONE,e.ONE_MINUS_SRC_ALPHA);let t=vo(e,e.VERTEX_SHADER,ga),n=vo(e,e.FRAGMENT_SHADER,xa),a=va(e,t,n);e.useProgram(a);let o=e.createBuffer();if(!o)throw new Error("metal-fx: gl.createBuffer returned null");e.bindBuffer(e.ARRAY_BUFFER,o),e.bufferData(e.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),e.STATIC_DRAW);let i=e.getAttribLocation(a,"a_position");e.enableVertexAttribArray(i),e.vertexAttribPointer(i,2,e.FLOAT,!1,0,0);let r={};for(let s of ba)r[s]=e.getUniformLocation(a,s);let l=e.createTexture();return l&&(e.activeTexture(e.TEXTURE0),e.bindTexture(e.TEXTURE_2D,l),e.texImage2D(e.TEXTURE_2D,0,e.RGBA,1,1,0,e.RGBA,e.UNSIGNED_BYTE,new Uint8Array([0,0,0,255])),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_MIN_FILTER,e.LINEAR),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_MAG_FILTER,e.LINEAR),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_WRAP_S,e.CLAMP_TO_EDGE),e.texParameteri(e.TEXTURE_2D,e.TEXTURE_WRAP_T,e.CLAMP_TO_EDGE),r.u_image&&e.uniform1i(r.u_image,0)),{program:a,buffer:o,uniforms:r,dummyTexture:l}}function no(){if(x)return x;let e=Math.min(ra,typeof window<"u"&&window.devicePixelRatio||1),t=Math.round(aa*e),n=typeof OffscreenCanvas<"u",a,o;if(n)a=new OffscreenCanvas(t,t),o=a.getContext("webgl2",{alpha:!0,premultipliedAlpha:!0,antialias:!1});else{let d=document.createElement("canvas");d.width=t,d.height=t,o=d.getContext("webgl2",{alpha:!0,premultipliedAlpha:!0,antialias:!1,preserveDrawingBuffer:!0}),a=d}if(!o)throw new Error("metal-fx: WebGL2 not supported");let{program:i,buffer:r,uniforms:l,dummyTexture:s}=wo(o),c=d=>{d.preventDefault(),x&&(x.contextLost=!0)},u=()=>{if(!x)return;let d=wo(x.gl);x.program=d.program,x.buffer=d.buffer,x.uniforms=d.uniforms,x.dummyTexture=d.dummyTexture,x.presetDirty=!0,x.contextLost=!1,Vt?.()};return a.addEventListener("webglcontextlost",c,!1),a.addEventListener("webglcontextrestored",u,!1),x={glCanvas:a,gl:o,program:i,buffer:r,uniforms:l,dummyTexture:s,preset:Ct.chromatic.modes.dark,presetDirty:!0,contextLost:!1,useOffscreen:n,frameBitmap:null,startMs:performance.now(),pausedMs:0,pausedAtMs:null,rafId:0,dpr:e,instances:new Set,frameCount:0,glowQueue:[],glowIdx:0,glowSkip:0,glowPixels:new Uint8Array(t*t*4),glowPixelsW:t,glowPixelsH:t},x}function ya(){var e;if(!x)return;let{gl:t,program:n,buffer:a,frameBitmap:o,dummyTexture:i}=x;try{o?.close(),t.deleteBuffer(a),t.deleteProgram(n),i&&t.deleteTexture(i),(e=t.getExtension("WEBGL_lose_context"))==null||e.loseContext()}catch{}x=null}var bo=0;function Ma(){if(!x)return;let e=performance.now();if(e-bo<oa)return;bo=e;let{gl:t,glCanvas:n}=x,a=n.width,o=n.height;(x.glowPixelsW!==a||x.glowPixelsH!==o)&&(x.glowPixelsW=a,x.glowPixelsH=o,x.glowPixels=new Uint8Array(a*o*4)),t.readPixels(0,0,a,o,t.RGBA,t.UNSIGNED_BYTE,x.glowPixels)}var Pe={bx:0,by:0};function kt(e,t,n){if(!x)return Pe.bx=0,Pe.by=0,Pe;let{glCanvas:a}=x,o=a.width,i=a.height,r=e.dpr,l=e.cssWidth*r,s=e.cssHeight*r,c=an*r,u=rn*r,d=l*(o/c)/e.shaderScale,m=s*(i/u)/e.shaderScale;d>o&&(d=o),m>i&&(m=i);let p=(o-d)/2,g=(i-m)/2,f=p+t/e.cssWidth*d,y=g+n/e.cssHeight*m;return Pe.bx=Math.round(f),Pe.by=Math.round(i-1-y),Pe}var fe={r:0,g:0,b:0,lum:0,count:0};function cn(e,t,n,a,o,i){let r=Math.max(1,i|0),l=Math.max(0,a-r),s=Math.min(t,a+r+1),c=Math.max(0,o-r),u=Math.min(n,o+r+1);fe.r=0,fe.g=0,fe.b=0,fe.lum=0,fe.count=0;for(let d=c;d<u;d++){let m=d*t;for(let p=l;p<s;p++){let g=(m+p)*4;fe.r+=e[g],fe.g+=e[g+1],fe.b+=e[g+2],fe.lum+=(.2126*e[g]+.7152*e[g+1]+.0722*e[g+2])/255,fe.count++}}return fe}var ee={r:255,g:255,b:255};function Gt(e,t,n,a){if(!x)return 0;let o=kt(e,t,n),i=cn(x.glowPixels,x.glowPixelsW,x.glowPixelsH,o.bx,o.by,a);return i.count>0?i.lum/i.count:0}function un(e,t,n,a){if(!x)return ee.r=255,ee.g=255,ee.b=255,ee;let o=kt(e,t,n),i=cn(x.glowPixels,x.glowPixelsW,x.glowPixelsH,o.bx,o.by,a);return i.count===0?(ee.r=255,ee.g=255,ee.b=255,ee):(ee.r=i.r/i.count,ee.g=i.g/i.count,ee.b=i.b/i.count,ee)}function _a(e,t,n,a){if(!x)return ee.r=255,ee.g=255,ee.b=255,ee;let o=kt(e,t,n),{glowPixels:i,glowPixelsW:r,glowPixelsH:l}=x,s=Math.max(1,a|0),c=Math.max(0,o.bx-s),u=Math.min(r,o.bx+s+1),d=Math.max(0,o.by-s),m=Math.min(l,o.by+s+1),p=-1;ee.r=255,ee.g=255,ee.b=255;for(let g=d;g<m;g++){let f=g*r;for(let y=c;y<u;y++){let b=(f+y)*4,v=i[b],h=i[b+1],M=i[b+2],w=Math.max(v,h,M),E=Math.min(v,h,M),F=(w>0?(w-E)/w:0)*(.35+.65*(w/255));F>p&&(p=F,ee.r=v,ee.g=h,ee.b=M)}}return ee}var pe={r:255,g:255,b:255,lum:0};function Sa(e,t,n,a){if(pe.r=255,pe.g=255,pe.b=255,pe.lum=0,!x)return pe;let o=kt(e,t,n),{glowPixels:i,glowPixelsW:r,glowPixelsH:l}=x,s=Math.max(1,a|0),c=Math.max(0,o.bx-s),u=Math.min(r,o.bx+s+1),d=Math.max(0,o.by-s),m=Math.min(l,o.by+s+1);for(let p=d;p<m;p++){let g=p*r;for(let f=c;f<u;f++){let y=(g+f)*4,b=(.2126*i[y]+.7152*i[y+1]+.0722*i[y+2])/255;b>pe.lum&&(pe.lum=b,pe.r=i[y],pe.g=i[y+1],pe.b=i[y+2])}}return pe}var At=14,yo=1.5,Ot={x:0,y:0};function He(e=512){return{xy:new Float32Array(e*2),n:0}}function Xe(e,t,n,a,o,i,r=He()){o=Math.max(0,Math.min(o,Math.min(n,a)/2));let l=4*(At+1)+Math.ceil(2*(n+a)/yo)+8;r.xy.length<l*2&&(r.xy=new Float32Array(l*2));let s=r.xy,c=0,u=(p,g)=>{i?(i(p,g,Ot),s[c*2]=Ot.x,s[c*2+1]=Ot.y):(s[c*2]=p,s[c*2+1]=g),c++},d=(p,g,f,y)=>{let b=Math.hypot(f-p,y-g),v=Math.max(1,Math.ceil(b/yo));for(let h=0;h<v;h++){let M=h/v;u(p+(f-p)*M,g+(y-g)*M)}},m=(p,g,f,y)=>{for(let b=0;b<=At;b++){let v=f+(y-f)*(b/At);u(p+o*Math.cos(v),g+o*Math.sin(v))}};return d(e+o,t,e+n-o,t),m(e+n-o,t+o,-Math.PI/2,0),d(e+n,t+o,e+n,t+a-o),m(e+n-o,t+a-o,0,Math.PI/2),d(e+n-o,t+a,e+o,t+a),m(e+o,t+a-o,Math.PI/2,Math.PI),d(e,t+a-o,e,t+o),m(e+o,t+o,Math.PI,1.5*Math.PI),r.n=c,r}wa(()=>{x&&x.instances.size>0&&x.pausedAtMs===null&&lt()});typeof document<"u"&&document.addEventListener("visibilitychange",()=>{!x||x.pausedAtMs!==null||x.contextLost||(document.hidden?gn():x.instances.size>0&&lt())});function Ca(e){let t=no(),n=e.hostCanvas.getContext("2d",{alpha:!0});if(!n)throw new Error("metal-fx: canvas 2D context unavailable");let a=e.scale??1,o={canvas:e.hostCanvas,ctx:n,cssWidth:e.cssWidth,cssHeight:e.cssHeight,cornerRadius:e.cornerRadius,kind:e.kind,ringCssPx:e.ringCssPx??(e.kind==="circle"?2:1)*a,shaderScale:e.shaderScale??(e.kind==="circle"?ln:sn)*a,opacityMul:e.opacityMul??1,glowGain:e.glowGain??1,visible:!0,paused:e.paused??!1,everCopied:!1,frozen:null,dpr:typeof window<"u"&&window.devicePixelRatio||1,scale:a,onAfterFrame:e.onAfterFrame,onComposite:e.onComposite,onFirstCopy:e.onFirstCopy,mask:e.mask??null,deform:null,deformLayers:null,overscan:0,cursorLight:null,glowFast:!1,rawCanvas:null,wantRaw:!1,ringCanvas:null,wantRing:!1};return ao(o),t.instances.add(o),t.rafId===0&&t.pausedAtMs===null&&lt(),o}function Ra(e){if(!x)return;x.instances.delete(e);let t=x.glowQueue.indexOf(e);t!==-1&&x.glowQueue.splice(t,1),x.instances.size===0&&(gn(),ya())}function ka(e){x&&(x.glowQueue.includes(e)||x.glowQueue.push(e))}function Ta(e){if(!x)return;let t=x.glowQueue.indexOf(e);t!==-1&&x.glowQueue.splice(t,1)}function Ne(e,t){let n=!1;t.mask!==void 0&&(e.mask=t.mask),t.cssWidth!==void 0&&t.cssWidth!==e.cssWidth&&(e.cssWidth=t.cssWidth,n=!0),t.cssHeight!==void 0&&t.cssHeight!==e.cssHeight&&(e.cssHeight=t.cssHeight,n=!0),t.cornerRadius!==void 0&&(e.cornerRadius=t.cornerRadius),t.scale!==void 0&&(e.scale=t.scale),t.kind!==void 0&&t.kind!==e.kind&&(e.kind=t.kind,t.shaderScale===void 0&&(e.shaderScale=(t.kind==="circle"?ln:sn)*e.scale),t.ringCssPx===void 0&&(e.ringCssPx=(t.kind==="circle"?2:1)*e.scale)),t.shaderScale!==void 0&&(e.shaderScale=t.shaderScale),t.ringCssPx!==void 0&&(e.ringCssPx=t.ringCssPx),t.opacityMul!==void 0&&(e.opacityMul=t.opacityMul),t.glowGain!==void 0&&(e.glowGain=t.glowGain),t.paused!==void 0&&t.paused!==e.paused&&(e.paused=t.paused,t.paused?mn(e):e.frozen=null,!t.paused&&x&&x.rafId===0&&x.pausedAtMs===null&&!x.contextLost&&lt()),n&&ao(e)}function Ea(e,t){e.visible=t,t&&x&&x.rafId===0&&x.pausedAtMs===null&&!x.contextLost&&lt()}function Aa(e){return(typeof window<"u"&&window.devicePixelRatio||1)===e.dpr?!1:(ao(e),fn(e),!0)}var dn=null;function Oa(e,t){let n=no();n.preset=dn??Ct[e].modes[t],n.presetDirty=!0}function hn(e){let t=no();dn=e,e&&(t.preset=e,t.presetDirty=!0)}var Oe=null;function Ba(e){Oe=e}function Bt(e,t){!Oe||!x||!e.visible||e.paused||x.glowQueue.includes(e)&&(e.glowFast=!!Oe(e,t))}function ao(e){e.dpr=typeof window<"u"&&window.devicePixelRatio||1;let t=e.overscan,n=Math.max(1,Math.round((e.cssWidth+2*t)*e.dpr)),a=Math.max(1,Math.round((e.cssHeight+2*t)*e.dpr));e.canvas.width!==n&&(e.canvas.width=n),e.canvas.height!==a&&(e.canvas.height=a);let o=e.canvas.style;t>0?(o.left=`${-t}px`,o.top=`${-t}px`,o.width=`calc(100% + ${2*t}px)`,o.height=`calc(100% + ${2*t}px)`,o.borderRadius="0"):o.left!==""&&(o.left="",o.top="",o.width="100%",o.height="100%",o.borderRadius="")}function Ia(e){let{ctx:t,dpr:n,canvas:a}=e,o=e.ringCssPx*n,i=a.width,r=a.height,l=Math.max(0,(e.cornerRadius-e.ringCssPx)*n);t.save(),t.globalCompositeOperation="destination-out",t.fillStyle="#000",t.beginPath(),t.roundRect(o,o,i-2*o,r-2*o,l),t.fill(),t.restore()}var Fa=He();function Te(e,t,n,a,o,i,r,l){let{xy:s,n:c}=Xe(t,n,a,o,i,r,Fa);e.beginPath();for(let u=0;u<c;u++)u===0?e.moveTo(s[0]*l,s[1]*l):e.lineTo(s[u*2]*l,s[u*2+1]*l);e.closePath()}function mn(e){if(!x)return null;let t=x.frameBitmap??x.glCanvas,n=x.glCanvas.width,a=x.glCanvas.height;if(n<1||a<1)return null;let o=e.frozen;o||(o=document.createElement("canvas"),e.frozen=o),(o.width!==n||o.height!==a)&&(o.width=n,o.height=a);let i=o.getContext("2d");return i?(i.clearRect(0,0,n,a),i.drawImage(t,0,0),o):(e.frozen=null,null)}function fn(e){var t,n;if(!x)return;let a=(e.paused?e.frozen??mn(e):null)??x.frameBitmap??x.glCanvas,o=e.dpr,i=e.canvas.width,r=e.canvas.height;if(i<1||r<1)return;let l=Math.max(1,Math.round(e.cssWidth*o)),s=Math.max(1,Math.round(e.cssHeight*o)),c=e.overscan*o,u=a.width,d=a.height,m=an*o,p=rn*o,g=l*(u/m)/e.shaderScale,f=s*(d/p)/e.shaderScale;g>u&&(g=u),f>d&&(f=d);let y=Math.max(0,(u-g)/2),b=Math.max(0,(d-f)/2),v=e.opacityMul*x.preset.shaderOpacity,h=e.ctx;h.clearRect(0,0,i,r);let M=e.deform;if(e.mask){if(v<1&&(h.globalAlpha=v),h.drawImage(a,y,b,g,f,0,0,i,r),v<1&&(h.globalAlpha=1),e.wantRaw){let w=e.rawCanvas;w||(w=document.createElement("canvas"),e.rawCanvas=w),(w.width!==i||w.height!==r)&&(w.width=i,w.height=r);let E=w.getContext("2d");E&&(E.clearRect(0,0,i,r),E.drawImage(e.canvas,0,0))}h.save(),h.globalCompositeOperation="destination-in",h.fillStyle="#000",e.mask(h,i,r,o),h.restore(),h.globalCompositeOperation="source-over"}else if(!M)v<1&&(h.globalAlpha=v),h.drawImage(a,y,b,g,f,0,0,i,r),v<1&&(h.globalAlpha=1),Ia(e);else{let w=e.cssWidth,E=e.cssHeight,F=e.cornerRadius,L=e.ringCssPx,A=e.deformLayers;h.save(),h.translate(c,c);let Y=l/g,P=s/f,$=Math.min(u,g*(l+2*c)/l),C=Math.min(d,f*(s+2*c)/s),V=Math.max(0,(u-$)/2),q=Math.max(0,(d-C)/2),W=$*Y,k=C*P;if(v<1&&(h.globalAlpha=v),h.drawImage(a,V,q,$,C,l/2-W/2,s/2-k/2,W,k),v<1&&(h.globalAlpha=1),h.globalCompositeOperation="destination-in",Te(h,0,0,w,E,F,M,o),h.fillStyle="#000",h.fill(),h.globalCompositeOperation="destination-out",Te(h,L,L,w-2*L,E-2*L,Math.max(0,F-L),M,o),h.fill(),e.wantRing){let _=e.ringCanvas;_||(_=document.createElement("canvas"),e.ringCanvas=_),(_.width!==i||_.height!==r)&&(_.width=i,_.height=r);let R=_.getContext("2d");R&&(R.setTransform(1,0,0,1,0,0),R.globalCompositeOperation="source-over",R.clearRect(0,0,i,r),R.translate(c,c),v<1&&(R.globalAlpha=v),R.drawImage(a,V,q,$,C,l/2-W/2,s/2-k/2,W,k),R.globalAlpha=1,R.globalCompositeOperation="destination-out",Te(R,L,L,w-2*L,E-2*L,Math.max(0,F-L),M,o),R.fillStyle="#000",R.fill(),R.globalCompositeOperation="source-over",R.setTransform(1,0,0,1,0,0))}if(A!=null&&A.hairline){let _=A.hairline;h.globalCompositeOperation="destination-over",Te(h,_.inset,_.inset,w-2*_.inset,E-2*_.inset,Math.max(0,F-_.inset),M,o),h.lineWidth=_.width*o,h.strokeStyle=_.color,h.stroke()}if(A!=null&&A.fill&&(h.globalCompositeOperation="destination-over",Te(h,0,0,w,E,F,M,o),h.fillStyle=A.fill,h.fill()),A!=null&&A.rim){let _=A.rim;h.globalCompositeOperation="source-over",h.save(),Te(h,0,0,w,E,F,M,o),h.clip();let R=_.inset+_.width/2;Te(h,R,R,w-2*R,E-2*R,Math.max(0,F-R),M,o),h.lineWidth=_.width*o,h.strokeStyle=_.color,h.stroke(),h.restore()}h.restore(),h.globalCompositeOperation="source-over"}if((t=e.onComposite)==null||t.call(e),e.onFirstCopy){let w=e.onFirstCopy;e.onFirstCopy=void 0,w()}(n=e.onAfterFrame)==null||n.call(e)}function La(){if(!x)return;let{gl:e,uniforms:t,preset:n,glCanvas:a,dpr:o}=x;t.u_resolution&&e.uniform2f(t.u_resolution,a.width,a.height),t.u_pixelRatio&&e.uniform1f(t.u_pixelRatio,o),t.u_colorBack&&e.uniform4fv(t.u_colorBack,go(n.colorBack)),t.u_colorTint&&e.uniform4fv(t.u_colorTint,go(n.colorTint)),t.u_repetition&&e.uniform1f(t.u_repetition,n.repetition),t.u_softness&&e.uniform1f(t.u_softness,n.softness),t.u_shiftRed&&e.uniform1f(t.u_shiftRed,n.shiftRed),t.u_shiftBlue&&e.uniform1f(t.u_shiftBlue,n.shiftBlue),t.u_distortion&&e.uniform1f(t.u_distortion,n.distortion),t.u_contour&&e.uniform1f(t.u_contour,n.contour),t.u_angle&&e.uniform1f(t.u_angle,n.angle),t.u_shape&&e.uniform1f(t.u_shape,n.shape),t.u_isImage&&e.uniform1i(t.u_isImage,0),t.u_imageAspectRatio&&e.uniform1f(t.u_imageAspectRatio,1),t.u_originX&&e.uniform1f(t.u_originX,n.originX),t.u_originY&&e.uniform1f(t.u_originY,n.originY),t.u_worldWidth&&e.uniform1f(t.u_worldWidth,n.worldWidth),t.u_worldHeight&&e.uniform1f(t.u_worldHeight,n.worldHeight),t.u_fit&&e.uniform1f(t.u_fit,n.fit),t.u_scale&&e.uniform1f(t.u_scale,n.scale),t.u_rotation&&e.uniform1f(t.u_rotation,n.rotation),t.u_offsetX&&e.uniform1f(t.u_offsetX,n.offsetX),t.u_offsetY&&e.uniform1f(t.u_offsetY,n.offsetY),x.presetDirty=!1}function Pa(e){if(!x)return;let{gl:t,uniforms:n,preset:a,glCanvas:o}=x,i=(e-x.startMs-x.pausedMs)/1e3*a.speed;t.viewport(0,0,o.width,o.height),t.clearColor(0,0,0,0),t.clear(t.COLOR_BUFFER_BIT),x.presetDirty&&La(),n.u_time&&t.uniform1f(n.u_time,i),t.drawArrays(t.TRIANGLES,0,6),x.frameCount++}var Mo=0;function pn(e){var t;if(!x)return;if(x.contextLost){x.rafId=0;return}let n=!1;for(let a of x.instances)if(a.visible&&(!a.paused||!a.everCopied)){n=!0;break}if(!n){x.rafId=0;return}if(x.rafId=requestAnimationFrame(pn),e-Mo<ea){if(Oe)for(let a of x.glowQueue)a.glowFast&&a.visible&&!a.paused&&(a.glowFast=!!Oe(a,e));return}Mo=e,Pa(e),Ma(),x.useOffscreen&&((t=x.frameBitmap)==null||t.close(),x.frameBitmap=x.glCanvas.transferToImageBitmap());for(let a of x.instances)a.visible&&(a.paused&&a.everCopied||(fn(a),a.everCopied=!0));if(Oe&&x.glowQueue.length>0&&++x.glowSkip%na===0)for(let a of x.glowQueue)a.visible&&!a.paused&&(a.glowFast=!!Oe(a,e))}function lt(){!x||x.rafId!==0||(x.rafId=requestAnimationFrame(pn))}function gn(){x&&(x.rafId!==0&&cancelAnimationFrame(x.rafId),x.rafId=0)}var Wt={linear:e=>e,smoothstep:e=>e*e*(3-2*e)};function je(e,t,n,a=Wt.linear){return{from:e,to:t,dur:n,ease:a,startMs:-1,val:e,done:!1}}function Qe(e,t){e.startMs=t,e.val=e.from,e.done=!1}function _o(e,t){if(e.done||e.startMs<0)return e.val;let n=Math.min(1,(t-e.startMs)/e.dur);return e.val=e.from+(e.to-e.from)*e.ease(n),n>=1&&(e.done=!0),e.val}var Na=Object.freeze({haloOpMul:2,extraIntensity:3.51,peakOp:.85,baseOp:.34,inset:1.5,extraOutward:1,wanderRange:15,wanderLerp:.0075,fadeRate:.00875,lumLo:.08,lumHi:.32,minDwellMs:1500,relocFadeMs:300,relocFadeOutMs:450,pointGain:2.5,haloHalfLen:7.8,extraHalfLen:9.13952/3,haloStrokeXl:26.4,haloStrokeLg:15.6,haloStrokeMd:7.2,haloStrokeSm:3,haloBlurXl:8.4,haloBlurLg:4.8,haloBlurMd:2.1,haloBlurSm:.9,haloOpXl:.385,haloOpLg:.595,haloOpMd:.7,haloOpSm:.7,extraStrokeOuter:4/3,extraStrokeCore:2/3,extraBlurOuter:2/3,extraBlurCore:1.35/3,extraFadeR:13/3,extraOpOuter:.85}),S={...Na},So=new Set;function Ua(e){return So.add(e),()=>{So.delete(e)}}var za=Object.freeze({enabled:!0,reach:56,fadeMs:200,cursor:!0,cursorDistance:186,cursorStrength:3.35,cursorDiffuse:1.4,cursorFalloff:37,cursorDepth:.4,cursorEdge:0,cursorReach:11.5,cursorBlur:.5,cursorZoom:3,spill:!1,spillRadius:48,spillStrength:.55,spillOffset:.35,spillLumGain:.7,spillSaturation:1.3,spillInside:.5,spillBlur:0,catchLight:!1,catchFollow:.25,catchGain:1}),Je={...za};var Ge=null,bt=null,Co=0;function Da(){let e=window.devicePixelRatio||1;return Co>0?Co/e:1}function xn(e,t){if(!me||!Ge)return;let n=Da(),a=(e-Ge.hotX*n).toFixed(2),o=(t-Ge.hotY*n).toFixed(2);me.style.transform=n===1?`translate3d(${a}px,${o}px,0)`:`translate3d(${a}px,${o}px,0) scale(${n.toFixed(4)})`}var vn=!1,wn=0,ft=0,pt=null,gt={x:0,y:0},xt=null,Ro=0;function $a(e,t,n,a,o){if(xt&&Ro===n&&xt.length===a*o)return xt;let i=document.createElement("canvas");i.width=a,i.height=o;let r=i.getContext("2d",{willReadFrequently:!0});if(!r)return null;r.scale(n,n),r.drawImage(e,0,0,t.width,t.height);let l=r.getImageData(0,0,a,o).data,s=new Uint8ClampedArray(a*o);for(let c=0,u=3;c<s.length;c++,u+=4)s[c]=l[u]>=128?255:0;return xt=s,Ro=n,s}function ko(e,t,n,a){let o=e.getImageData(0,0,t,n),i=o.data;for(let r=0,l=0,s=3;r<n;r++)for(let c=0;c<t;c++,l++,s+=4){let u=i[s];if(u===0)continue;let d=a(c,r,l);i[s]=d>=1?u:d<=0?0:u*d}e.putImageData(o,0,0)}function Va(e,t){if(!pt)return 0;let n=-1/0;for(let a=0;a<pt.length;a+=2){let o=pt[a]*e+pt[a+1]*t;o>n&&(n=o)}return n===-1/0?0:n}var et=0,Ye=!1,Be=0,Ht=0,xe=Number.NaN,Ce=Number.NaN,nt=0,at=0,Ee=0,Ae=0,Z=null,G={d:0,nx:0,ny:0,k:1,left:0,top:0},It={x:0,y:0},ve={r:255,g:255,b:255},ye=null,Xt="",Yt=-1,qt=-1,rt=!1;function Ga(){et++,Ha()}function Wa(){et=Math.max(0,et-1),et===0&&Xa()}var Ke=e=>typeof window.matchMedia=="function"&&window.matchMedia(e).matches;function To(){if(vn||performance.now()<wn||!Ge||!bt||Ke("(prefers-reduced-motion: reduce)")||Ke("(forced-colors: active)")||!Ke("(pointer: fine)")||!Ke("(hover: hover)"))return!1;let e=window.visualViewport;return!(e&&Math.abs(e.scale-1)>.001)}function Ha(){Ye||et===0||typeof document>"u"||Ke("(pointer: fine)")&&(Ye=!0,document.addEventListener("pointermove",bn,{passive:!0}),document.addEventListener("pointerleave",Re),document.addEventListener("pointercancel",Re),document.addEventListener("keydown",yn,{passive:!0}),document.addEventListener("visibilitychange",Re),window.addEventListener("blur",Re))}function Xa(){Ye&&(Ye=!1,document.removeEventListener("pointermove",bn),document.removeEventListener("pointerleave",Re),document.removeEventListener("pointercancel",Re),document.removeEventListener("keydown",yn),document.removeEventListener("visibilitychange",Re),window.removeEventListener("blur",Re),Be!==0&&(cancelAnimationFrame(Be),Be=0),Z&&(Z.cursorLight=null,Z=null),Ee=0,Ae=0,ye&&(ye.remove(),ye=null,Xt="",Yt=-1,qt=-1,rt=!1),Fe(),me&&(me.remove(),me=null))}var jt=!0,ro=!1;function bn(e){jt=e.pointerType==="mouse"||e.pointerType==="",ro=!1,xe=nt=e.clientX,Ce=at=e.clientY,it&&me&&(jt&&_n(xe,Ce)?xn(xe,Ce):Fe()),Mn()}function yn(){ro=!0,Fe()}function Re(){xe=Ce=Number.NaN,Mn()}function Mn(){!Ye||Be!==0||(Ht=performance.now(),Be=requestAnimationFrame(Sn))}function Ya(e,t,n,a,o,i,r){let l=i==="circle"?Math.min(n,a)/2:Math.max(0,Math.min(o,Math.min(n,a)/2)),s=n/2,c=a/2,u=Math.max(0,n/2-l),d=Math.max(0,a/2-l),m=Math.max(-u,Math.min(u,e-s)),p=Math.max(-d,Math.min(d,t-c)),g=e-s-m,f=t-c-p,y=Math.hypot(g,f);if(y>1e-6)return r.x=s+m+g/y*l,r.y=c+p+f/y*l,y-l;let b=e,v=n-e,h=t,M=a-t,w=Math.min(b,v,h,M);return w===b?(r.x=0,r.y=t):w===v?(r.x=n,r.y=t):w===h?(r.x=e,r.y=0):(r.x=e,r.y=a),-w}var me=null,_e=null,Qt=null,de=null,Ze=null,Eo=!1,Ao=0,Oo=0,Bo=0,it=!1,Ve=!1,Jt="",be=null,tt="",qa=/^(INPUT|TEXTAREA|SELECT)$/,Kt=new WeakMap,Io=0,Zt=null;function ja(e){let t=e;for(;t&&t!==document.body;){if(qa.test(t.tagName)||t.isContentEditable)return!0;t=t.parentElement}return!1}function Qa(){if(me)return!0;let e=document.createElement("div");e.className="metal-fx-cursor",e.setAttribute("aria-hidden","true"),e.style.cssText="position:fixed;left:0;top:0;pointer-events:none;z-index:2147483001;will-change:transform;transform-origin:0 0;display:none";let t=document.createElement("canvas");t.style.display="block",e.appendChild(t),document.body.appendChild(e);let n=t.getContext("2d"),a=document.createElement("canvas"),o=a.getContext("2d");return!n||!o?(e.remove(),!1):(me=e,_e=t,Qt=n,de=a,Ze=o,!0)}function _n(e,t,n=!1){let a=performance.now();if(!n&&Ve&&a-Io<12)return!0;Io=a;let o=document.elementFromPoint(e,t);if(!o)return eo(),!1;if(o===Zt&&Ve)return!0;Zt=o;let i=Kt.get(o);if(i===void 0){if(i=!ja(o),i){let r=getComputedStyle(o).cursor;i=r==="auto"||r==="default"||r==="none"}Kt.set(o,i)}if(!i)return eo(),!1;if(!Ve){let r=document.documentElement;Jt=r.style.cursor,r.style.cursor="none",Ve=!0}return o!==be&&(be&&(be.style.cursor=tt,be=null,tt=""),getComputedStyle(o).cursor!=="none"&&(be=o,tt=o.style.cursor,o.style.cursor="none")),!0}function eo(){be&&(be.isConnected&&(be.style.cursor=tt),be=null,tt=""),Ve&&(document.documentElement.style.cursor=Jt,Ve=!1,Jt=""),Zt=null,Kt=new WeakMap}function Fe(){eo(),me&&it&&(me.style.display="none",it=!1)}function Ja(e,t,n){if(!Qt||!Ze||!_e||!de||!me||!Ge||!bt)return;let a=Ge,o=Math.min(3,window.devicePixelRatio||1);if((o!==Ao||a.width!==Oo||a.height!==Bo)&&(Ao=o,Oo=a.width,Bo=a.height,_e.width=de.width=Math.ceil(a.width*o),_e.height=de.height=Math.ceil(a.height*o),_e.style.width=`${a.width}px`,_e.style.height=`${a.height}px`),!Eo&&(Ze=de.getContext("2d",{willReadFrequently:!0}),Eo=!0,!Ze))return;let i=Qt,r=Ze,l=a.width,s=a.height;i.setTransform(1,0,0,1,0,0),i.clearRect(0,0,_e.width,_e.height),i.scale(o,o),i.drawImage(bt,0,0,l,s);let c=G.left+G.nx*G.k,u=G.top+G.ny*G.k,d=nt-a.hotX+gt.x,m=at-a.hotY+gt.y,p=c-d,g=u-m,f=Math.hypot(p,g),y=f>.01?p/f:1,b=f>.01?g/f:0,v=Va(y,b)+t.cursorEdge,h=Math.max(0,f-v),M=Math.max(1,t.cursorFalloff),w=1/(1+h/M*(h/M)),E=e.cssWidth/2,F=e.cssHeight/2,L=E-G.nx,A=F-G.ny,Y=Math.hypot(L,A)||1,P=e.mask?0:e.ringCssPx*.5+1,$=G.nx+L/Y*P,C=G.ny+A/Y*P,V=Sa(e,$,C,4),q=V.lum,W=V.r,k=V.g,_=V.b,R=t.cursorStrength*w*n,J=t.cursorDiffuse*w*(.5+.5*Math.min(1,q/.5))*n;if(f>.01&&R+J>.005){let Q=p/f,te=g/f,I=Math.atan2(te,Q),O=Math.max(.1,Math.min(1,t.cursorDepth)),D=gt.x+v*Q,U=gt.y+v*te,N=Math.max(1,t.cursorReach);if(r.setTransform(1,0,0,1,0,0),r.clearRect(0,0,de.width,de.height),r.scale(o,o),R>.005){r.save(),r.filter=t.cursorBlur>0?`blur(${t.cursorBlur}px)`:"none";let ne=Math.max(1,t.cursorZoom);r.translate(D,U),r.rotate(I),r.scale(-1,1),r.translate((f-v)*O,0),r.rotate(-I),r.scale(ne,ne);let ae=e.overscan,oe=G.k,ie=Math.max(1,Math.ceil(R));r.globalAlpha=Math.min(1,R/ie),r.globalCompositeOperation="lighter";let ce=e.mask&&e.rawCanvas?e.rawCanvas:e.canvas;for(let j=0;j<ie;j++)r.drawImage(ce,-(G.nx+ae)*oe,-(G.ny+ae)*oe,(e.cssWidth+2*ae)*oe,(e.cssHeight+2*ae)*oe);r.restore();let se=1/o,B=1/N;ko(r,de.width,de.height,(j,X)=>{let le=-(((j+.5)*se-D)*Q+((X+.5)*se-U)*te);return le<=0?1:1-le*B})}if(J>.005){let ne=Math.max(W,k,_)||1,ae=Math.round(W*255/ne),oe=Math.round(k*255/ne),ie=Math.round(_*255/ne),ce=N*1.2,se=r.createLinearGradient(D+.5*Q,U+.5*te,D-ce*Q,U-ce*te),B=Math.min(1,J);se.addColorStop(0,`rgba(${ae},${oe},${ie},${B.toFixed(3)})`),se.addColorStop(.45,`rgba(${ae},${oe},${ie},${(B*.4).toFixed(3)})`),se.addColorStop(1,`rgba(${ae},${oe},${ie},0)`),r.globalCompositeOperation="lighter",r.fillStyle=se,r.fillRect(0,0,l,s),r.globalCompositeOperation="source-over"}let re=$a(bt,a,o,de.width,de.height);re&&ko(r,de.width,de.height,(ne,ae,oe)=>re[oe]===0?0:1),i.globalCompositeOperation="lighter",i.drawImage(de,0,0,l,s),i.globalCompositeOperation="source-over"}xn(nt,at),it||(me.style.display="",it=!0)}function Ka(){if(ye)return ye;let e=document.createElement("div");return e.className="metal-fx-cursor-spill",e.setAttribute("aria-hidden","true"),e.style.cssText="position:fixed;left:0;top:0;pointer-events:none;z-index:2147483000;border-radius:50%;mix-blend-mode:plus-lighter;will-change:transform,opacity;opacity:0;display:none",document.body.appendChild(e),ye=e,e}function to(){!ye||!rt||(ye.style.display="none",ye.style.opacity="0",rt=!1)}function Sn(e){if(Be=0,!Ye)return;let t=performance.now();try{Za(e)}catch(n){vn=!0,Fe(),to(),Z&&(Z.cursorLight=null,Z=null),typeof console<"u"&&console.warn("metal-fx: cursor light disabled after error",n);return}performance.now()-t>6?++ft>=20&&(ft=0,wn=performance.now()+5e3,Fe()):ft>0&&ft--}function Za(e){let t=Je,n=Math.min(.05,Math.max(.001,(e-Ht)/1e3));Ht=e;let a=null,o=0,i=0;if(t.enabled&&x&&!Number.isNaN(xe)){let l=Number.POSITIVE_INFINITY,s=Math.max(1,t.reach),c=t.cursor&&To()?Math.max(1,t.cursorDistance):0,u=Math.max(s,c);for(let d of x.instances){if(!d.visible||!d.canvas.isConnected)continue;let m=d.canvas.getBoundingClientRect();if(m.width<=0)continue;let p=d.overscan,g=m.width/(d.cssWidth+2*p),f=m.left+p*g,y=m.top+p*g,b=u*g;if(xe<f-b||xe>f+d.cssWidth*g+b||Ce<y-b||Ce>y+d.cssHeight*g+b)continue;let v=(xe-f)/g,h=(Ce-y)/g,M=Ya(v,h,d.cssWidth,d.cssHeight,d.cornerRadius,d.kind,It),w=Math.abs(M);w<=u&&w<l&&(l=w,a=d,G.d=M,G.nx=It.x,G.ny=It.y,G.k=g,G.left=f,G.top=y)}if(a){if(l<=s){let d=1-l/s;o=d*d*(3-2*d)}l<=c&&(i=Math.min(1,(1-l/c)*3)),a.mask&&(G.nx=a.cssWidth/2,G.ny=a.cssHeight/2,a.wantRaw=!0)}}let r=1-Math.exp(-(n*1e3)/(Math.max(1,t.fadeMs)/3));if(Ee+=(o-Ee)*r,Ae+=(i-Ae)*r,a&&a!==Z&&(Z&&(Z.cursorLight=null,Bt(Z,e)),Z=a),!a&&Ee<.002&&Ae<.002){Ee=0,Ae=0,Z&&(Z.cursorLight=null,Bt(Z,e),Z=null),to(),Fe();return}if(Z){if(t.catchLight){let l=Z.cursorLight??(Z.cursorLight={x:0,y:0,w:0});l.x=G.nx,l.y=G.ny,l.w=Ee}else Z.cursorLight&&(Z.cursorLight=null);if(Bt(Z,e),t.cursor&&Ae>.002&&jt&&!ro&&!Number.isNaN(xe)&&To()&&Qa()&&_n(xe,Ce)?Ja(Z,t,Ae):Fe(),t.spill){let l=Ka(),s=un(Z,G.nx,G.ny,2),c=Gt(Z,G.nx,G.ny,3),u=Math.max(s.r,s.g,s.b)||1,d=on(s.r*255/u,s.g*255/u,s.b*255/u),[m,p,g]=nn(d[0],Math.min(1,d[1]*t.spillSaturation),1);ve.r+=(m-ve.r)*.15,ve.g+=(p-ve.g)*.15,ve.b+=(g-ve.b)*.15;let f=Math.round(ve.r/6)*6,y=Math.round(ve.g/6)*6,b=Math.round(ve.b/6)*6,v=`radial-gradient(closest-side, rgba(${f},${y},${b},1) 0%, rgba(${f},${y},${b},0.35) 45%, rgba(${f},${y},${b},0) 100%)`;v!==Xt&&(Xt=v,l.style.background=v);let h=Math.max(1,t.spillRadius*G.k);h!==Yt&&(Yt=h,l.style.width=`${(2*h).toFixed(1)}px`,l.style.height=`${(2*h).toFixed(1)}px`),t.spillBlur!==qt&&(qt=t.spillBlur,l.style.filter=t.spillBlur>0?`blur(${t.spillBlur}px)`:"");let M=G.left+G.nx*G.k,w=G.top+G.ny*G.k,E=nt+(M-nt)*t.spillOffset,F=at+(w-at)*t.spillOffset;l.style.transform=`translate3d(${(E-h).toFixed(2)}px,${(F-h).toFixed(2)}px,0)`;let L=Math.min(1,Math.max(0,c/.3)),A=1-t.spillLumGain+t.spillLumGain*L,Y=G.d<0?t.spillInside:1,P=Math.max(0,Math.min(1,t.spillStrength*Ee*A*Y));rt||(l.style.display="",rt=!0),l.style.opacity=P.toFixed(3)}else to();Be=requestAnimationFrame(Sn)}}var Mt=new Map;function er(e,t){let n=Math.sqrt(12*e*e/t+1),a=Math.floor(n);a%2===0&&a--;let o=a+2,i=(12*e*e-t*a*a-4*t*a-3*t)/(-4*a-4),r=Math.round(i),l=[];for(let s=0;s<t;s++)l.push(s<r?a:o);return l}function tr(e,t,n,a,o){let i=1/(o+o+1);for(let r=0;r<a;r++){let l=r*n,s=0;for(let c=-o;c<=o;c++)s+=e[l+Math.min(n-1,Math.max(0,c))];for(let c=0;c<n;c++){t[l+c]=s*i;let u=l+Math.max(0,c-o),d=l+Math.min(n-1,c+o+1);s+=e[d]-e[u]}}}function or(e,t,n,a,o){let i=1/(o+o+1);for(let r=0;r<n;r++){let l=0;for(let s=-o;s<=o;s++)l+=e[Math.min(a-1,Math.max(0,s))*n+r];for(let s=0;s<a;s++){t[s*n+r]=l*i;let c=Math.max(0,s-o)*n+r,u=Math.min(a-1,s+o+1)*n+r;l+=e[u]-e[c]}}}function Tt(e,t,n,a){if(a<=.05)return e;let o=new Float32Array(e.length),i=e;for(let r of er(a,3)){let l=(r-1)/2;tr(i,o,t,n,l),or(o,i,t,n,l)}return i}function nr(e,t,n,a,o,i,r){let l=document.createElement("canvas");l.width=n,l.height=a;let s=l.getContext("2d",{willReadFrequently:!0}),c=new Float32Array(n*a);if(!s)return c;s.scale(o,o),s.strokeStyle="#fff",s.lineCap="round",s.lineJoin="round",s.lineWidth=t,s.beginPath(),s.moveTo(i-e,r),s.lineTo(i+e,r),s.stroke();let u=s.getImageData(0,0,n,a).data;for(let d=0,m=3;d<c.length;d++,m+=4)c[d]=u[m]/255;return c}function Cn(e,t,n,a,o){let i=0;for(let f of e)i=Math.max(i,(f.stroke/2+3*f.blur)*n);let r=Math.ceil(i)+1,l=2*t+2*r,s=2*r,c=Math.ceil(l*a),u=Math.ceil(s*a),d=new Float32Array(c*u);for(let f of e){let y=nr(t,f.stroke*n,c,u,a,r,r);y=Tt(y,c,u,f.blur*n*a);let b=f.opacity;for(let v=0;v<d.length;v++){let h=y[v]*b;d[v]=d[v]+h*(1-d[v])}}if(o>0){let f=r*a,y=r*a,b=o*n*a;for(let v=0;v<u;v++)for(let h=0;h<c;h++){let M=Math.hypot(h+.5-f,v+.5-y)/b,w;M<=.3?w=1:M<=.65?w=1-(M-.3)/.35*.75:M<1?w=.25*(1-(M-.65)/.35):w=0,d[v*c+h]*=w}}let m=document.createElement("canvas");m.width=c,m.height=u;let p=m.getContext("2d"),g=new Uint8ClampedArray(c*u);for(let f=0;f<d.length;f++)g[f]=Math.round(Math.min(1,d[f])*255);if(p){let f=p.createImageData(c,u),y=f.data;for(let b=0,v=0;b<d.length;b++,v+=4)y[v]=255,y[v+1]=255,y[v+2]=255,y[v+3]=g[b];p.putImageData(f,0,0)}return{canvas:m,alpha:g,w:l,h:s,ax:r,ay:r}}function Rn(){return[S.haloStrokeXl,S.haloStrokeLg,S.haloStrokeMd,S.haloStrokeSm,S.haloBlurXl,S.haloBlurLg,S.haloBlurMd,S.haloBlurSm,S.haloOpXl,S.haloOpLg,S.haloOpMd,S.haloOpSm,S.extraStrokeOuter,S.extraStrokeCore,S.extraBlurOuter,S.extraBlurCore,S.extraFadeR,S.extraOpOuter].join(",")}function ar(e,t,n){let a=`h|${e.toFixed(2)}|${t}|${n}|${Rn()}`,o=Mt.get(a);return o||(o=Cn([{stroke:S.haloStrokeXl,blur:S.haloBlurXl,opacity:S.haloOpXl},{stroke:S.haloStrokeLg,blur:S.haloBlurLg,opacity:S.haloOpLg},{stroke:S.haloStrokeMd,blur:S.haloBlurMd,opacity:S.haloOpMd},{stroke:S.haloStrokeSm,blur:S.haloBlurSm,opacity:S.haloOpSm}],e,t,n,0),Mt.set(a,o)),o}function rr(e,t,n){let a=`e|${e.toFixed(2)}|${t}|${n}|${Rn()}`,o=Mt.get(a);return o||(o=Cn([{stroke:S.extraStrokeOuter,blur:S.extraBlurOuter,opacity:S.extraOpOuter},{stroke:S.extraStrokeCore,blur:S.extraBlurCore,opacity:1}],e,t,n,S.extraFadeR),Mt.set(a,o)),o}function Fo(e,t,n,a,o){var i;let r=t<<16|n<<8|a;if(o.canvas&&o.tint===r&&o.src===e)return o.canvas;let l=o.canvas,s=o.img;(!l||!s||o.src!==e)&&(l=document.createElement("canvas"),l.width=e.canvas.width,l.height=e.canvas.height,s=((i=l.getContext("2d"))==null?void 0:i.createImageData(l.width,l.height))??null);let c=l.getContext("2d");if(c&&s){let u=s.data,d=e.alpha;for(let m=0,p=0;m<d.length;m++,p+=4)u[p]=t,u[p+1]=n,u[p+2]=a,u[p+3]=d[m];c.putImageData(s,0,0)}return o.canvas=l,o.img=s,o.tint=r,o.src=e,l}function io(e,t,n){let a=Math.max(0,Math.min(n,Math.min(e,t)/2));return 2*Math.max(0,e-2*a)+2*Math.max(0,t-2*a)+2*Math.PI*a}function _t(e,t,n,a){return a==="circle"?2*Math.PI*Math.max(0,Math.min(n,Math.min(e,t)/2)):io(e,t,n)}function st(e,t,n,a,o,i,r,l){let s=l||{x:0,y:0},c=Math.max(0,Math.min(a,Math.min(t,n)/2));if(r==="circle"){let b=2*Math.PI*c;if(b<=1e-4)return s.x=t*.5,s.y=n*.5,s;e=(e%b+b)%b;let v=-Math.PI/2+e/b*Math.PI*2,h=Math.max(0,c-o+i);return s.x=t*.5+h*Math.cos(v),s.y=n*.5+h*Math.sin(v),s}let u=Math.max(0,t-2*c),d=Math.max(0,n-2*c),m=Math.PI*c/2,p=2*(u+d)+4*m;e=(e%p+p)%p;let g=Math.max(0,c-o+i),f=e;if(f<u)return s.x=c+f,s.y=o-i,s;if(f-=u,f<m){let b=-Math.PI/2+(m>0?f/m:0)*(Math.PI/2);return s.x=t-c+g*Math.cos(b),s.y=c+g*Math.sin(b),s}if(f-=m,f<d)return s.x=t-o+i,s.y=c+f,s;if(f-=d,f<m){let b=(m>0?f/m:0)*(Math.PI/2);return s.x=t-c+g*Math.cos(b),s.y=n-c+g*Math.sin(b),s}if(f-=m,f<u)return s.x=t-c-f,s.y=n-o+i,s;if(f-=u,f<m){let b=Math.PI/2+(m>0?f/m:0)*(Math.PI/2);return s.x=c+g*Math.cos(b),s.y=n-c+g*Math.sin(b),s}if(f-=m,f<d)return s.x=o-i,s.y=n-c-f,s;f-=d;let y=Math.PI+(m>0?f/m:0)*(Math.PI/2);return s.x=c+g*Math.cos(y),s.y=c+g*Math.sin(y),s}function ir(e,t,n,a,o,i){let r=Math.max(0,Math.min(o,Math.min(n,a)/2));if(i==="circle"){let w=2*Math.PI*r;return w<=1e-4?0:((Math.atan2(t-a/2,e-n/2)+Math.PI/2)/(2*Math.PI)*w%w+w)%w}let l=Math.max(0,n-2*r),s=Math.max(0,a-2*r),c=Math.PI*r/2,u=Math.PI/2,d=l,m=d+c,p=m+s,g=p+c,f=g+l,y=f+c,b=y+s,v=e>=r&&e<=n-r,h=t>=r&&t<=a-r;if(v&&h){let w=e,E=n-e,F=t,L=a-t,A=Math.min(w,E,F,L);return A===F?e-r:A===E?m+(t-r):A===L?g+(n-r-e):y+(a-r-t)}if(v)return t<a/2?e-r:g+(n-r-e);if(h)return e>n/2?m+(t-r):y+(a-r-t);if(e>n/2&&t<a/2){let w=Math.atan2(t-r,e-(n-r));return d+(w+u)/u*c}if(e>n/2){let w=Math.atan2(t-(a-r),e-(n-r));return p+w/u*c}if(t>a/2){let w=Math.atan2(t-(a-r),e-r);return f+(w-u)/u*c}let M=Math.atan2(t-r,e-r);return b+(M+Math.PI)/u*c}var Ft={x:0,y:0},Lt={x:0,y:0};function sr(e,t,n,a,o,i){return st(e-.1,t,n,a,o,0,i,Ft),st(e+.1,t,n,a,o,0,i,Lt),Math.atan2(Lt.y-Ft.y,Lt.x-Ft.x)}function Lo(e,t,n){if(e===t)return n<e?0:1;let a=Math.max(0,Math.min(1,(n-e)/(t-e)));return a*a*(3-2*a)}function lr(e){if(e.samplePoints&&e.samplePoints.length>0)return e.samplePoints.map((o,i)=>({x:o.x,y:o.y,arc:i}));let t=_t(e.width,e.height,e.cornerRadius,e.kind),n=S.inset*(e.scale??1),a=[];for(let o=0;o<xo;o++){let i=o/xo*t,r=st(i,e.width,e.height,e.cornerRadius,n,0,e.kind);a.push({x:r.x,y:r.y,arc:i})}return a}var cr=.05,ur=120*(1e3/15),Po=1e3/15,No=2e3,Pt=400,dr=2.625,hr=1.008,mr=.31,kn=140,Tn=40,En=20,fr=34,vt=.25,pr=.01,Uo=.004,gr=.5,xr=3.5,he={x:0,y:0};function zo(e,t){let{width:n,height:a}=t,o=t.scale??1,i=Math.min(3,typeof window<"u"&&window.devicePixelRatio||1),r=_t(n,a,t.cornerRadius,t.kind)/io(kn,Tn,En),l=Math.max(1,S.haloHalfLen*r),s=Math.max(.6,S.extraHalfLen*r),c=ar(l,o,i),u=rr(s,o,i),d=Math.ceil(Math.max(c.ay,u.ay)+S.extraOutward*r*o+2),m=document.createElement("div");m.className="metal-fx-glow-svg",m.setAttribute("aria-hidden","true");let p=document.createElement("div");p.className="metal-fx-glow-env",p.style.cssText="position:absolute;inset:0;pointer-events:none;opacity:0";let g=document.createElement("canvas");g.className="metal-fx-glow-canvas";let f=n+2*d,y=a+2*d;g.width=Math.ceil(f*i),g.height=Math.ceil(y*i),g.style.cssText=`position:absolute;left:${-d}px;top:${-d}px;width:${f}px;height:${y}px;pointer-events:none`,p.appendChild(g),m.appendChild(p),e.appendChild(m);let b=g.getContext("2d",{willReadFrequently:!!t.maskDataUrl});if(!b)throw new Error("metal-fx: glow canvas 2D context unavailable");let v={wrap:m,env:p,canvas:g,ctx:b,surroundPath:null,bandPath:null,maskAlpha:null,maskReady:!1,margin:d,dpr:i,halo:c,extra:u,haloTint:{canvas:null,img:null,tint:-1,src:null},extraTint:{canvas:null,img:null,tint:-1,src:null},mO:He(),mI:He(),maskSum:Number.NaN,maskDeformed:!1,deform:null,width:n,height:a,cornerRadius:t.cornerRadius,kind:t.kind,scale:o,perim:lr(t),pointMode:!!(t.samplePoints&&t.samplePoints.length>0),currentIdx:0,appearedAt:0,glowOpacity:0,relocTween:null,relocNextIdx:-1,relocMul:0,envClock:0,cursorMode:!1,cursorArc:0,cursorTargetArc:0,lastTickMs:0,wanderS:0,wanderTargetS:0,wanderFrames:0,tintFrom:{r:255,g:255,b:255},tintTarget:{r:255,g:255,b:255},tintTween:null,tintHoldUntil:0,dX:Number.NaN,dY:Number.NaN,dAng:Number.NaN,dEX:Number.NaN,dEY:Number.NaN,dHOp:Number.NaN,dEOp:Number.NaN,dHaloTint:"",dExtraTint:"",dirty:!0,dEnv:-1};if(t.maskDataUrl){let h=new Image;h.onload=()=>{let M=document.createElement("canvas");M.width=g.width,M.height=g.height;let w=M.getContext("2d",{willReadFrequently:!0});if(!w)return;w.scale(i,i),w.drawImage(h,d,d,n,a);let E=w.getImageData(0,0,M.width,M.height).data,F=M.width*M.height,L=new Float32Array(F);for(let C=0,V=3;C<F;C++,V+=4)L[C]=E[V]/255;let A=Tt(Float32Array.from(L),M.width,M.height,xr*i),Y=0;for(let C=0;C<F;C++)A[C]>Y&&(Y=A[C]);let P=Y>0?gr/Y:0,$=new Uint8ClampedArray(F);for(let C=0;C<F;C++)$[C]=Math.round(Math.max(L[C],A[C]*P)*255);v.maskAlpha=$,v.maskReady=!0,v.dirty=!0},h.src=t.maskDataUrl}else oo(v,null);return v}function oo(e,t){if(e.pointMode)return;let{margin:n,width:a,height:o,cornerRadius:i}=e,r=e.kind==="circle"?2:1;Xe(0,0,a,o,i,t,e.mO),Xe(r,r,a-2*r,o-2*r,Math.max(0,i-r),t,e.mI);let l=new Path2D;Nt(l,e.mO,n);let s=new Path2D;Nt(s,e.mO,n),Nt(s,e.mI,n);let c=new Path2D;c.rect(0,0,a+2*n,o+2*n),c.addPath(l),e.surroundPath=c,e.bandPath=s,e.maskReady=!0}function Nt(e,t,n){let a=t.xy;for(let o=0;o<t.n;o++){let i=a[o*2]+n,r=a[o*2+1]+n;o===0?e.moveTo(i,r):e.lineTo(i,r)}e.closePath()}function vr(e,t){if(!e)return 0;Xe(0,0,t.width,t.height,t.cornerRadius,e,t.mO);let n=0,a=t.mO.xy;for(let o=0;o<t.mO.n;o+=4)n+=a[o*2]*1.37+a[o*2+1];return n}function wr(e,t){if(e.deform=t,!e.pointMode)if(t){let n=vr(t,e);n!==e.maskSum&&(e.maskSum=n,oo(e,t),e.maskDeformed=!0,e.dirty=!0)}else e.maskDeformed&&(e.maskSum=Number.NaN,oo(e,null),e.maskDeformed=!1,e.dirty=!0)}function br(e,t,n,a,o="dark"){var i;let{width:r,height:l,cornerRadius:s,perim:c}=e;if(c.length===0)return!1;let u=2,d=-1,m=e.currentIdx,p=0;for(let B=0;B<c.length;B++){let j=c[B],X=Gt(t,j.x,j.y,u);X>d&&(d=X,m=B),B===e.currentIdx&&(p=X)}let g=e.appearedAt>0&&n-e.appearedAt<S.minDwellMs,f=S.baseOp+(S.peakOp-S.baseOp)*Lo(S.lumLo,S.lumHi,p),y=!g&&d-p>cr,b=t.cursorLight,v=Je.enabled&&Je.catchLight&&!e.pointMode&&!!b&&b.w>.02,h=_t(r,l,s,e.kind);v&&(e.cursorTargetArc=ir(b.x,b.y,r,l,s,e.kind));let M=v?Math.min(1,S.peakOp*Je.catchGain*b.w):0,w=e.lastTickMs>0?Math.min(200,Math.max(.5,n-e.lastTickMs)):Po;e.lastTickMs=n,e.envClock+=Math.min(w,fr);let E=B=>1-Math.pow(1-B,w/Po),F=Math.max(1,S.relocFadeMs),L=Math.max(1,S.relocFadeOutMs),A=-2,Y=-3,P=()=>{e.appearedAt=n,e.wanderS=0,e.wanderTargetS=0,e.wanderFrames=0,e.relocTween=je(0,1,F,Wt.smoothstep),Qe(e.relocTween,e.envClock)},$=B=>{e.relocNextIdx=B,e.relocTween=je(1,0,L,Wt.smoothstep),Qe(e.relocTween,e.envClock)};if((i=e.relocTween)!=null&&i.done&&e.relocTween.to===0){let B=e.relocNextIdx;if(B===A&&!v&&(B=Y),B===Y)e.cursorMode=!1,e.appearedAt=0,e.relocTween=null;else if(B===A)e.cursorMode=!0,e.cursorArc=e.cursorTargetArc,e.glowOpacity=M,P();else{e.currentIdx=B;let j=c[e.currentIdx],X=Gt(t,j.x,j.y,u);e.glowOpacity=S.baseOp+(S.peakOp-S.baseOp)*Lo(S.lumLo,S.lumHi,X),P()}}if((!e.relocTween||e.relocTween.done)&&(e.appearedAt===0?(v?(e.cursorMode=!0,e.cursorArc=e.cursorTargetArc,e.glowOpacity=M):(e.cursorMode=!1,e.currentIdx=m,e.glowOpacity=f),P()):v!==e.cursorMode?$(v?A:Y):!e.cursorMode&&y&&$(m)),e.cursorMode){v&&(e.glowOpacity=M);let B=Math.max(.01,Math.min(1,Je.catchFollow)),j=1-Math.pow(1-B,w/(1e3/60)),X=e.cursorTargetArc-e.cursorArc;X=(X%h+h*1.5)%h-h/2,e.cursorArc+=X*j}else e.glowOpacity+=(f-e.glowOpacity)*E(S.fadeRate);e.glowOpacity=Math.max(0,Math.min(1,e.glowOpacity)),e.relocMul=e.relocTween?_o(e.relocTween,e.envClock):1;let C=_t(r,l,s,e.kind)/io(kn,Tn,En),V=S.wanderRange*C;e.wanderFrames+=w,e.wanderFrames>=ur&&(e.wanderTargetS=(Math.random()*2-1)*V,e.wanderFrames=0),e.wanderS+=(e.wanderTargetS-e.wanderS)*E(S.wanderLerp);let q,W,k,_,R;if(e.pointMode){let B=c[e.currentIdx];q=B.x+e.wanderS,W=B.y,k=0,_=q,R=W}else{let B=e.cursorMode?e.cursorArc:c[e.currentIdx].arc+e.wanderS,j=S.inset*e.scale;st(B,r,l,s,j,0,e.kind,he),q=he.x,W=he.y,k=sr(B,r,l,s,j,e.kind);let X=S.extraOutward*C*e.scale;st(B,r,l,s,j,X,e.kind,he),_=he.x,R=he.y}e.deform&&(e.deform(q,W,he),q=he.x,W=he.y,e.deform(_,R,he),_=he.x,R=he.y);let J=o==="light",Q=J?_a(t,q,W,u):un(t,q,W,u);e.tintTween?e.tintTween.done&&(J?(e.tintFrom={r:e.tintFrom.r+(e.tintTarget.r-e.tintFrom.r)*e.tintTween.val,g:e.tintFrom.g+(e.tintTarget.g-e.tintFrom.g)*e.tintTween.val,b:e.tintFrom.b+(e.tintTarget.b-e.tintFrom.b)*e.tintTween.val},e.tintTarget={...Q},e.tintTween=je(0,1,Pt),Qe(e.tintTween,n)):n>=e.tintHoldUntil&&(e.tintFrom={...e.tintTarget},e.tintTarget={...Q},e.tintTween=je(0,1,Pt),Qe(e.tintTween,n),e.tintHoldUntil=n+No)):(e.tintFrom={...Q},e.tintTarget={...Q},e.tintTween=je(0,1,Pt),Qe(e.tintTween,n),e.tintHoldUntil=J?0:n+No),_o(e.tintTween,n);let te=e.tintTween.val,I,O,D;if(J)I=Math.round(e.tintFrom.r+(e.tintTarget.r-e.tintFrom.r)*te),O=Math.round(e.tintFrom.g+(e.tintTarget.g-e.tintFrom.g)*te),D=Math.round(e.tintFrom.b+(e.tintTarget.b-e.tintFrom.b)*te);else{let B=e.tintFrom.r+(e.tintTarget.r-e.tintFrom.r)*te,j=e.tintFrom.g+(e.tintTarget.g-e.tintFrom.g)*te,X=e.tintFrom.b+(e.tintTarget.b-e.tintFrom.b)*te,le=Math.max(B,j,X)||1;I=Math.round(255*(B/le)),O=Math.round(255*(j/le)),D=Math.round(255*(X/le))}let U=`rgb(${I},${O},${D})`,N="#ffffff";if(J){let B=on(I,O,D),[j,X,le]=nn(B[0],Math.min(1,B[1]*dr),Math.max(mr,B[2]*hr));N=`rgb(${j},${X},${le})`}let re=Math.max(0,Math.min(1,a))*(e.pointMode?S.pointGain:1),ne=Math.min(1,e.glowOpacity*S.haloOpMul*re),ae=Math.min(1,e.glowOpacity*S.extraIntensity*re);if(Math.abs(e.relocMul-e.dEnv)>.002){let B=e.relocMul>=.998&&e.dEnv<.998;e.dEnv=e.relocMul,e.env.style.opacity=e.relocMul.toFixed(3),B&&(e.dirty=!0)}let oe=!!(e.relocTween&&!e.relocTween.done)||e.cursorMode,ie=!(Math.abs(q-e.dX)<vt&&Math.abs(W-e.dY)<vt&&Math.abs(k-e.dAng)<pr&&Math.abs(_-e.dEX)<vt&&Math.abs(R-e.dEY)<vt),ce=!(Math.abs(ne-e.dHOp)<Uo&&Math.abs(ae-e.dEOp)<Uo),se=U!==e.dHaloTint||N!==e.dExtraTint;return(e.dirty||ie||ce||se)&&(e.dX=q,e.dY=W,e.dAng=k,e.dEX=_,e.dEY=R,e.dHOp=ne,e.dEOp=ae,e.dHaloTint=U,e.dExtraTint=N,e.dirty=!1,yr(e,q,W,k,_,R,ne,ae,U,N)),oe}function yr(e,t,n,a,o,i,r,l,s,c){let{ctx:u,canvas:d,dpr:m,margin:p}=e;if(u.setTransform(1,0,0,1,0,0),u.globalCompositeOperation="source-over",u.globalAlpha=1,u.clearRect(0,0,d.width,d.height),r<=.002&&l<=.002||!e.maskReady)return;let g=r>.002?Fo(e.halo,...Do(s),e.haloTint):null,f=l>.002?c==="#ffffff"?e.extra.canvas:Fo(e.extra,...Do(c),e.extraTint):null,y=M=>{g&&(u.save(),u.translate(t+p,n+p),u.rotate(a),u.globalAlpha=r*M,u.drawImage(g,-e.halo.ax,-e.halo.ay,e.halo.w,e.halo.h),u.restore()),f&&(u.save(),u.translate(o+p,i+p),u.rotate(a),u.globalAlpha=l*M,u.drawImage(f,-e.extra.ax,-e.extra.ay,e.extra.w,e.extra.h),u.restore())};if(!e.pointMode&&e.surroundPath&&e.bandPath){u.save(),u.scale(m,m),u.clip(e.surroundPath,"evenodd"),y(.5),u.restore(),u.save(),u.scale(m,m),u.clip(e.bandPath,"evenodd"),y(1),u.restore();return}u.save(),u.scale(m,m),y(1),u.restore();let b=e.maskAlpha;if(!b)return;let v=u.getImageData(0,0,d.width,d.height),h=v.data;for(let M=0,w=3;M<b.length;M++,w+=4){let E=b[M];if(E!==255){if(E===0){h[w]=0;continue}h[w]=(h[w]*E+127)/255}}u.putImageData(v,0,0)}var Ue=[255,255,255];function Do(e){if(e[0]==="#")return Ue[0]=parseInt(e.slice(1,3),16),Ue[1]=parseInt(e.slice(3,5),16),Ue[2]=parseInt(e.slice(5,7),16),Ue;let t=4,n=0,a=0;for(;t<e.length&&a<3;){let o=e.charCodeAt(t++);o>=48&&o<=57?n=n*10+(o-48):(o===44||o===41)&&(Ue[a++]=n,n=0)}return Ue}function Mr(e,t){e.pointMode===t.pointMode&&(t.currentIdx=Math.min(e.currentIdx,Math.max(0,t.perim.length-1)),t.appearedAt=e.appearedAt,t.glowOpacity=e.glowOpacity,t.relocTween=e.relocTween,t.relocNextIdx=e.relocNextIdx<0?e.relocNextIdx:Math.min(e.relocNextIdx,Math.max(0,t.perim.length-1)),t.relocMul=e.relocMul,t.envClock=e.envClock,t.cursorMode=e.cursorMode,t.cursorArc=e.cursorArc,t.cursorTargetArc=e.cursorTargetArc,t.lastTickMs=e.lastTickMs,t.wanderS=e.wanderS,t.wanderTargetS=e.wanderTargetS,t.wanderFrames=e.wanderFrames,t.tintFrom=e.tintFrom,t.tintTarget=e.tintTarget,t.tintTween=e.tintTween,t.tintHoldUntil=e.tintHoldUntil,t.dEnv=e.relocMul,t.env.style.opacity=e.relocMul.toFixed(3))}var $o=Object.freeze({offsetY:1,blur:.5,alpha:.9,color:"#ffffff"});function _r(e,t,n){let a=Math.min(3,typeof window<"u"&&window.devicePixelRatio||1),o=Math.ceil(3*n.blur+Math.abs(n.offsetY)+1),i=t.width+2*o,r=t.height+2*o,l=document.createElement("canvas");l.className="metal-fx-rim-canvas",l.setAttribute("aria-hidden","true"),l.width=Math.ceil(i*a),l.height=Math.ceil(r*a),l.style.cssText=`position:absolute;left:${-o}px;top:${-o}px;width:${i}px;height:${r}px;pointer-events:none`;let s=l.getContext("2d"),c=document.createElement("canvas");c.width=l.width,c.height=l.height;let u=c.getContext("2d",{willReadFrequently:!0});if(!s||!u)return null;e.appendChild(l);let d={canvas:l,ctx:s,scratch:c,sctx:u,width:t.width,height:t.height,cornerRadius:t.cornerRadius,kind:t.kind,ring:t.ring,margin:o,dpr:a,opts:n,mO:He(),mI:He(),sum:Number.NaN};return An(d,null,!0),d}function Vo(e,t,n){let a=t.xy;for(let o=0;o<t.n;o++){let i=a[o*2]+n,r=a[o*2+1]+n;o===0?e.moveTo(i,r):e.lineTo(i,r)}e.closePath()}function An(e,t,n=!1){let{width:a,height:o,cornerRadius:i,ring:r,margin:l,dpr:s}=e;Xe(0,0,a,o,i,t,e.mO),Xe(r,r,a-2*r,o-2*r,Math.max(0,i-r),t,e.mI);let c=0,u=e.mO.xy;for(let C=0;C<e.mO.n;C+=4)c+=u[C*2]*1.37+u[C*2+1];if(!n&&c===e.sum)return;e.sum=c;let{sctx:d,scratch:m,ctx:p,canvas:g,opts:f}=e,y=m.width,b=m.height;d.setTransform(1,0,0,1,0,0),d.clearRect(0,0,y,b),d.scale(s,s),d.fillStyle="#fff",d.beginPath(),Vo(d,e.mO,l),Vo(d,e.mI,l),d.fill("evenodd");let v=d.getImageData(0,0,y,b).data,h=y*b,M=new Float32Array(h);for(let C=0,V=3;C<h;C++,V+=4)M[C]=v[V]/255;let w=Math.round(f.offsetY*s)*y,E=new Float32Array(h);if(w>=0)for(let C=0;C<h;C++)E[C]=Math.max(0,M[C]-(C>=w?M[C-w]:0));else for(let C=0;C<h;C++)E[C]=Math.max(0,M[C]-(C-w<h?M[C-w]:0));let F=Tt(E,y,b,f.blur*s),L=parseInt(f.color.slice(1,3),16),A=parseInt(f.color.slice(3,5),16),Y=parseInt(f.color.slice(5,7),16),P=p.createImageData(y,b),$=P.data;for(let C=0,V=0;C<h;C++,V+=4)$[V]=L,$[V+1]=A,$[V+2]=Y,$[V+3]=Math.round(Math.min(1,F[C]*M[C]*f.alpha)*255);p.setTransform(1,0,0,1,0,0),p.putImageData(P,0,0)}function Go(e){e&&e.canvas.remove()}var yt=12,Wo=32,Ho=1,Xo=.55,Sr=1,Cr=1,Rr=.85,kr=0,Tr=1.3,Yo=3.6,Er=.7,Ar=1,Or=.52,Br=1,Ir=.044,Fr=235,Lr=2.535,qo=.7,Pr=.5,Nr=new Set(["INPUT","TEXTAREA","SELECT","OPTION"]);function Ur(e,t){let n=Math.max(e.left-t.right,t.left-e.right,0),a=Math.max(e.top-t.bottom,t.top-e.bottom,0);return Math.sqrt(n*n+a*a)}function zr(e,t,n,a){return!(Math.min(e.bottom,t.bottom)-Math.max(e.top,t.top)<n||Math.max(e.left-t.right,t.left-e.right,0)>a)}function Dr(e,t,n,a){return Math.min(e.right,t.right)-Math.max(e.left,t.left)<n?!1:Math.max(e.top-t.bottom,t.top-e.bottom,0)<=a}function Ie(e,t,n,a,o,i){let r=Math.max(0,Math.min(i,a*.5,o*.5)),l=e.roundRect;if(typeof l=="function"){l.call(e,t,n,a,o,r);return}e.moveTo(t+r,n),e.lineTo(t+a-r,n),e.quadraticCurveTo(t+a,n,t+a,n+r),e.lineTo(t+a,n+o-r),e.quadraticCurveTo(t+a,n+o,t+a-r,n+o),e.lineTo(t+r,n+o),e.quadraticCurveTo(t,n+o,t,n+o-r),e.lineTo(t,n+r),e.quadraticCurveTo(t,n,t+r,n)}function On(e,t,n,a,o){if(!o.flipX&&!o.flipY){e.drawImage(t,o.sx??0,o.sy??0,n,a,o.x,o.y,o.w,o.h);return}e.save(),o.flipX&&(e.translate(o.x+o.w,0),e.scale(-1,1)),o.flipY&&(e.translate(0,o.y+o.h),e.scale(1,-1)),e.drawImage(t,o.sx??0,o.sy??0,n,a,o.flipX?0:o.x,o.flipY?0:o.y,o.w,o.h),e.restore()}var $r=4;function Vr(e,t,n,a,o,i,r){if(a<=2*r||o<=2*r){e.beginPath(),Ie(e,t,n,a,o,i),e.clip();return}e.beginPath(),Ie(e,t,n,a,o,i),Ie(e,t+r,n+r,a-2*r,o-2*r,Math.max(0,i-r)),e.clip("evenodd")}function Gr(e,t,n,a,o,i,r,l,s,c,u,d){let m=d??Math.max(1,Math.round((yt+$r*3)*u)),p=Math.max(0,r),g=!0;for(let f=0;f<3&&p>1e-4;f++){let y=Math.min(1,p);e.save(),Vr(e,c.x,c.y,c.w,c.h,c.r,m),e.globalCompositeOperation=g?"source-over":"lighter",g=!1,e.globalAlpha=y,On(e,t,n,a,s),e.globalAlpha=1,e.globalCompositeOperation="destination-in",e.fillStyle=l,e.fillRect(0,0,o,i),e.restore(),p-=y}}function Bn(e,t,n,a,o,i,r){let l=r|0;if(l<1||a<=2*l||o<=2*l){e.beginPath(),Ie(e,t,n,a,o,i),e.clip();return}e.beginPath(),Ie(e,t,n,a,o,i),Ie(e,t+l,n+l,a-2*l,o-2*l,Math.max(0,i-l)),e.clip("evenodd")}function Wr(e,t,n,a,o,i,r,l,s,c,u,d){let m=l*u,p=!0;for(let g=0;g<3&&m>1e-4;g++){let f=Math.min(1,m);e.save(),Bn(e,r.x,r.y,r.w,r.h,r.r,s),e.globalCompositeOperation=p?"source-over":"lighter",p=!1,e.globalAlpha=f,On(e,t,n,a,d),e.globalAlpha=1,e.globalCompositeOperation="destination-in",e.fillStyle=c,e.fillRect(0,0,o,i),e.restore(),m-=f}}function Hr(e,t,n,a,o,i,r,l){let s=e.createLinearGradient(a,o,i,r);s.addColorStop(0,`rgba(255,255,255,${l.toFixed(3)})`),s.addColorStop(.5,`rgba(255,255,255,${(l*.45).toFixed(3)})`),s.addColorStop(1,"rgba(255,255,255,0)"),e.save(),Bn(e,t.x,t.y,t.w,t.h,t.r,n),e.globalCompositeOperation="lighter",e.lineWidth=n*2,e.strokeStyle=s,e.beginPath(),Ie(e,t.x,t.y,t.w,t.h,t.r),e.stroke(),e.restore()}function In(e){let t=getComputedStyle(e),n=[parseFloat(t.borderTopLeftRadius)||0,parseFloat(t.borderTopRightRadius)||0,parseFloat(t.borderBottomRightRadius)||0,parseFloat(t.borderBottomLeftRadius)||0].filter(a=>a>0);return n.length?Math.min.apply(null,n):0}function Fn(e){let t=getComputedStyle(e),n=Math.max(parseFloat(t.borderTopWidth)||0,parseFloat(t.borderRightWidth)||0,parseFloat(t.borderBottomWidth)||0,parseFloat(t.borderLeftWidth)||0),a=0,o=0,i=t.boxShadow;if(i&&i!=="none"){let l=i.replace(/rgba?\([^)]*\)/g,u=>u.replace(/,/g,"\0")).split(/,\s*/),s=1/0,c=1/0;for(let u of l){let d=u.match(/-?\d+(?:\.\d+)?px/g);if(!d||d.length<4)continue;let m=parseFloat(d[3]);m>0&&(/\binset\b/.test(u)?m<s&&(s=m):m<c&&(c=m))}Number.isFinite(s)&&(a=s),Number.isFinite(c)&&(o=c)}let r=Math.max(n,o);return{width:Math.max(n,a,o)||1,outerCssPx:r}}function jo(e){e.cornerRadius=In(e.el);let t=Fn(e.el);e.hairlineWidth=t.width,e.hairlineOuterCssPx=t.outerCssPx}function Xr(e){typeof ResizeObserver<"u"&&(e.resizeObserver=new ResizeObserver(()=>jo(e)),e.resizeObserver.observe(e.el)),typeof MutationObserver<"u"&&(e.mutationObserver=new MutationObserver(()=>jo(e)),e.mutationObserver.observe(e.el,{attributes:!0,attributeFilter:["style","class"]}))}function Yr(e){var t,n;(t=e.resizeObserver)==null||t.disconnect(),e.resizeObserver=null,(n=e.mutationObserver)==null||n.disconnect(),e.mutationObserver=null}var ke=new Set,qr=Object.freeze({enabled:!0,radius:11.5,strength:.57,penumbra:.55,falloff:.21,edgeFade:.7,softness:.24,repaintMs:36}),Et={...qr};var Se=null,Ut=0,Qo=0,Jo=!1;function so(){Ut!==0||typeof requestAnimationFrame>"u"||(Ut=requestAnimationFrame(e=>{if(Ut=0,e-Qo<Et.repaintMs){so();return}Qo=e,Pn()}))}var St=!1;function jr(e,t){let n=Et.radius;for(let a of ke){let o=a.anchorEl.getBoundingClientRect(),i=a.el.getBoundingClientRect(),r=Math.min(o.left,i.left)-n,l=Math.max(o.right,i.right)+n,s=Math.min(o.top,i.top)-n,c=Math.max(o.bottom,i.bottom)+n;if(e>=r&&e<=l&&t>=s&&t<=c)return!0}return!1}function Ko(e){if(Se={x:e.clientX,y:e.clientY},!Et.enabled)return;let t=jr(e.clientX,e.clientY);(t||St)&&so(),St=t}function wt(){Se=null,St&&so(),St=!1}function Ln(e){typeof document>"u"||e===Jo||(Jo=e,e?(document.addEventListener("pointermove",Ko,{passive:!0}),document.addEventListener("pointerleave",wt),window.addEventListener("blur",wt)):(document.removeEventListener("pointermove",Ko),document.removeEventListener("pointerleave",wt),window.removeEventListener("blur",wt),Se=null))}function Qr(e,t,n,a,o,i,r,l,s){if(!Se)return;let c=Et;if(!c.enabled||c.strength<=0)return;let u=c.radius,d,m,p,g,f,y;if(o){let k=n.left>=a.right;d=k?a.right:n.right,m=k?n.left:a.left,p=Se.x,g=Se.y,f=Math.max(n.top,a.top),y=Math.min(n.bottom,a.bottom)}else{let k=n.top>=a.bottom;d=k?a.bottom:n.bottom,m=k?n.top:a.top,p=Se.y,g=Se.x,f=Math.max(n.left,a.left),y=Math.min(n.right,a.right)}let b=Math.min(d,m),v=Math.max(d,m),h=Math.max(1,v-b);if(p<b-u||p>v+u||g<f-u||g>y+u)return;let M=Math.max(0,Math.min(1,Math.abs(p-d)/h)),w=Math.max(.5,u*c.edgeFade),E=Math.min(1,Math.min(p-(b-u),v+u-p)/w),F=Math.min(1,Math.min(g-(f-u),y+u-g)/w),L=c.strength*(1-c.falloff*M)*E*F;if(L<=.001)return;let A=u*s*(1+c.penumbra*M),Y=o?(g-a.top+l)*s:(g-a.left+l)*s,P=Math.max(0,Math.min(.5,(1-c.softness)*.5)),$=Math.max(.001,.5-P),C=o?r:i,V=Math.max(0,Math.floor(Y-A)),q=Math.min(C,Math.ceil(Y+A));if(q<=V)return;let W=new Float32Array(q-V);for(let k=V;k<q;k++){let _=(k+.5-(Y-A))/(2*A),R=_<$?_/$:_>1-$?(1-_)/$:1;W[k-V]=1-L*Math.max(0,Math.min(1,R))}for(let k of[e,t]){let _=o?0:V,R=o?V:0,J=o?i:q-V,Q=o?q-V:r,te=k.getImageData(_,R,J,Q),I=te.data;if(o)for(let O=0;O<Q;O++){let D=W[O];if(!(D>=.999))for(let U=O*J*4+3,N=(O+1)*J*4;U<N;U+=4)I[U]=I[U]*D}else for(let O=0;O<Q;O++)for(let D=0;D<J;D++){let U=W[D];if(U>=.999)continue;let N=(O*J+D)*4+3;I[N]=I[N]*U}k.putImageData(te,_,R)}}var we=null,ze=null,De=null,$e=null;function Jr(e,t){return we||(we=document.createElement("canvas"),ze=document.createElement("canvas"),De=we.getContext("2d",{alpha:!0}),$e=ze.getContext("2d",{alpha:!0})),!De||!$e||!we||!ze?!1:(we.width!==e&&(we.width=e,ze.width=e),we.height!==t&&(we.height=t,ze.height=t),De.setTransform(1,0,0,1,0,0),$e.setTransform(1,0,0,1,0,0),De.globalCompositeOperation="source-over",$e.globalCompositeOperation="source-over",De.clearRect(0,0,e,t),$e.clearRect(0,0,e,t),!0)}function Kr(e,t,n,a=1){if(typeof document>"u"||Nr.has(e.tagName))return null;for(let g of ke)if(g.el===e)return g.strength=a,g;let o=document.createElement("div");o.setAttribute("data-metal-fx-reflection",""),o.setAttribute("aria-hidden","true");let i=document.createElement("canvas");i.className="metal-fx-reflection-canvas";let r=i.getContext("2d",{alpha:!0,willReadFrequently:!0});if(!r)return null;let l=document.createElement("canvas");l.className="metal-fx-reflection-stroke-canvas";let s=l.getContext("2d",{alpha:!0,willReadFrequently:!0});if(!s)return null;o.appendChild(i),o.appendChild(l);let c=getComputedStyle(e),u=!1;c.position==="static"&&(e.style.position="relative",u=!0);let d=!1;c.isolation!=="isolate"&&(e.style.isolation="isolate",d=!0),e.setAttribute("data-metal-fx-reflect-host",""),e.insertBefore(o,e.firstChild);let m=Fn(e),p={el:e,anchor:t,anchorEl:n,strength:a,wrap:o,canvas:i,ctx:r,strokeCanvas:l,strokeCtx:s,cornerRadius:In(e),hairlineWidth:m.width,hairlineOuterCssPx:m.outerCssPx,appliedPositionRelative:u,appliedIsolation:d,resizeObserver:null,mutationObserver:null};return Xr(p),ke.add(p),Ln(!0),p}function Zr(e){for(let t of ke)if(t.el===e){Yr(t),t.canvas.width=0,t.canvas.height=0,t.strokeCanvas.width=0,t.strokeCanvas.height=0,t.wrap.parentNode===t.el&&t.el.removeChild(t.wrap),t.el.removeAttribute("data-metal-fx-reflect-host"),t.appliedPositionRelative&&(t.el.style.position=""),t.appliedIsolation&&(t.el.style.isolation=""),ke.delete(t),ke.size===0&&Ln(!1);return}}function ei(e,t,n,a,o){if(a<1||o<1)return null;let i=e.getContext("2d");if(!i)return null;let r=i.getImageData(t,n,a,o).data,l=a,s=o,c=-1,u=-1;for(let d=0;d<o;d++){let m=d*a;for(let p=0;p<a;p++)r[(m+p)*4+3]>8&&(p<l&&(l=p),p>c&&(c=p),d<s&&(s=d),d>u&&(u=d))}return c<0?null:{x:t+l,y:n+s,w:c-l+1,h:u-s+1}}function Pn(){if(ke.size===0)return;let e=typeof window<"u"&&window.devicePixelRatio||1,t=new Map;for(let n of ke){let a=n.el.getBoundingClientRect(),o=t.get(n.anchorEl);if(o||(o=n.anchorEl.getBoundingClientRect(),t.set(n.anchorEl,o)),a.width<1||a.height<1||o.width<1||o.height<1)continue;let i=n.el.hasAttribute("data-metal-fx-text");if(i&&!n.glyphStyled&&(n.canvas.style.filter="blur(0.4px) saturate(1.35) brightness(1.2)",n.glyphStyled=!0),!zr(o,a,Ho,Wo)&&!Dr(o,a,Ho,Wo)){n.canvas.width!==1&&(n.canvas.width=1,n.canvas.height=1),n.strokeCanvas.width!==1&&(n.strokeCanvas.width=1,n.strokeCanvas.height=1);continue}let r=i&&!!n.anchor.mask;r&&!n.anchor.wantRaw&&(n.anchor.wantRaw=!0),n.anchor.wantRing||(n.anchor.wantRing=!0);let l=!!n.anchor.deform&&!!n.anchor.ringCanvas,s=r&&n.anchor.rawCanvas?n.anchor.rawCanvas:l?n.anchor.ringCanvas:n.anchor.canvas,c=Math.round(n.anchor.overscan*e),u=c,d=c,m=(s.width|0)-2*c,p=(s.height|0)-2*c;if(n.anchor.mask&&!r){let Q=ei(s,u,d,m,p);Q&&(u=Q.x,d=Q.y,m=Q.w,p=Q.h)}if(m<4||p<4)continue;let g=(o.left+o.right)*.5,f=(o.top+o.bottom)*.5,y=(a.left+a.right)*.5,b=(a.top+a.bottom)*.5,v=g-y,h=f-b,M=Math.max(o.left-a.right,a.left-o.right,0),w=Math.max(o.top-a.bottom,a.top-o.bottom,0),E=M>=w,F=Ur(o,a),L=1-Math.min(1,F/yt);L=L*L*(3-2*L);let A=Xo+(Sr-Xo)*L,Y=Math.min(Yo,A*Tr*Er)*n.strength,P=o.left>=a.left&&o.right<=a.right&&o.top>=a.top&&o.bottom<=a.bottom?[!0,!1]:[E],$=n.anchor.scale??1,C=Math.max(Ar*$,n.hairlineWidth),V=Math.max(1,Math.round(C*e)),q=Math.max(1,Math.round(Math.max(Br*$,n.hairlineWidth)*e)),W=n.hairlineOuterCssPx;n.wrap.style.inset=`${-W}px`,n.wrap.style.borderRadius=`${Math.max(0,n.cornerRadius)}px`;let k=Math.max(1,Math.round((a.width+W*2)*e)),_=Math.max(1,Math.round((a.height+W*2)*e));n.canvas.width!==k&&(n.canvas.width=k),n.canvas.height!==_&&(n.canvas.height=_),n.strokeCanvas.width!==k&&(n.strokeCanvas.width=k),n.strokeCanvas.height!==_&&(n.strokeCanvas.height=_);let R=n.ctx;R.setTransform(1,0,0,1,0,0),R.clearRect(0,0,k,_);let J=n.strokeCtx;J.setTransform(1,0,0,1,0,0),J.clearRect(0,0,k,_);for(let[Q,te]of P.entries()){let I=Q>0&&Jr(k,_),O=I?De:R,D=I?$e:J,U=Math.min((i?yt*1.5:yt)*e,Math.max(k,_)),N,re,ne,ae;te?(N=v>0?k:0,ne=v>0?k-U:U,re=_*.5,ae=_*.5):(re=h>0?_:0,ae=h>0?_-U:U,N=k*.5,ne=k*.5);let oe=R.createLinearGradient(N,re,ne,ae);oe.addColorStop(0,`rgba(0,0,0,${Cr})`),oe.addColorStop(.5,`rgba(0,0,0,${Rr})`),oe.addColorStop(1,`rgba(0,0,0,${kr})`);let ie=m/e,ce=i?Math.max(1,Math.min(te?k:_,Math.round(te?m:p))):Math.max(1,Math.round(Fr*Math.max(.1,ie/140)*e)),se,B,j,X,le=!1,qe=!1;if(te){let H=Math.max(o.top,a.top),K=Math.min(o.bottom,a.bottom);le=!0,se=v>0?k-ce:0,B=Math.round((H-a.top+W)*e),j=ce,X=Math.max(1,Math.round((K-H)*e))}else{let H=Math.max(o.left,a.left),K=Math.min(o.right,a.right);qe=!0,se=Math.round((H-a.left+W)*e),B=h>0?_-ce:0,j=Math.max(1,Math.round((K-H)*e)),X=ce}let ct={x:se,y:B,w:j,h:X,flipX:le,flipY:qe,sx:u,sy:d},Me={x:0,y:0,w:k,h:_,r:Math.max(0,n.cornerRadius*e)},T=i?Math.min(1,Y*qo):Math.min(Yo,Y*Lr*qo*Pr);Gr(O,s,m,p,k,_,T,oe,ct,Me,e,i?Math.max(k,_):void 0),i||(Wr(D,s,m,p,k,_,Me,Y,V,oe,Or,ct),Hr(D,Me,q,N,re,ne,ae,Math.min(.85,Ir*Y))),I&&(R.globalCompositeOperation="lighter",R.drawImage(we,0,0),J.globalCompositeOperation="lighter",J.drawImage(ze,0,0))}for(let Q of P)Qr(R,J,o,a,Q,k,_,W,e);R.globalCompositeOperation="source-over",J.globalCompositeOperation="source-over"}}var zt=!1,Zo=0;function ti(){zt||(zt=!0,!(typeof requestAnimationFrame>"u")&&requestAnimationFrame(e=>{zt=!1,!(e-Zo<ta)&&(Zo=e,Pn())}))}var en="metal-fx-styles",oi=`
.metal-fx-root {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  isolation: isolate;
  overflow: visible;
  background: #272727;
  color: #f8f8f8;
}
.metal-fx-root[data-theme='light'] {
  background: #ffffff;
  color: #1d1d1d;
}

.metal-fx-root::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 2;
  box-shadow: inset 0 0 50px 0 rgba(255, 255, 255, 0.02);
}
.metal-fx-root[data-theme='light']::before {
  box-shadow: inset 0 0 50px 0 rgba(0, 0, 0, 0.02);
}

.metal-fx-root::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 4;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
}
.metal-fx-root[data-theme='light']::after {
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.06);
}
/* Circle variant gets a thicker outer rim than the button variant. */
.metal-fx-root[data-variant='circle']::after {
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.1);
}
.metal-fx-root[data-theme='light'][data-variant='circle']::after {
  box-shadow: inset 0 0 0 2px rgba(0, 0, 0, 0.06);
}

.metal-fx-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  z-index: 0;
  pointer-events: none;
  border-radius: inherit;
}

/* The inner spacer \u2014 defines the inset geometry where the metal ring meets
   the interior (3 px for Button, 1-2 px for Circle) and carries the Circle dark
   hairline ('box-shadow: inset' rules below). Intentionally transparent so
   the wrapper's background propagates through to the punched shader centre,
   giving consumers a single surface tone to override. See "Single-surface
   background" in the file header for the rationale. */
.metal-fx-inner {
  position: absolute;
  inset: 3px;
  border-radius: inherit;
  z-index: 1;
  pointer-events: none;
}

.metal-fx-root[data-variant='button'][data-shape='pill'] .metal-fx-inner {
  border-radius: calc(var(--mfx-radius, 20px) - 3px);
}
.metal-fx-root[data-variant='button'][data-shape='circle'] .metal-fx-inner {
  border-radius: calc(var(--mfx-radius, 16px) - 3px);
}
.metal-fx-root[data-variant='circle'][data-shape='pill'] .metal-fx-inner {
  inset: 0;
  border-radius: var(--mfx-radius, 20px);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.45);
}
.metal-fx-root[data-variant='circle'][data-shape='circle'] .metal-fx-inner {
  inset: 0;
  border-radius: var(--mfx-radius, 16px);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.45);
}
/* Circle-variant hairline alpha \u2014 light mode.
   Source-of-truth: index.html L2261-2267. The 0.45-alpha black inset that
   reads as a single-pixel frame against the dark interior is too heavy
   on a #ffffff inner: it ends up looking like a hard 2-px black ring
   against the iridescent shader. Suppressed entirely (alpha 0) \u2014 the
   shader's own iridescent rim already defines the silhouette in light
   mode, so an extra dark hairline only competes with it. The rule is
   kept (rather than deleted) as a tunable hook in case a future variant
   wants to re-introduce a soft edge. NOTE: we keep the dark-mode inset
   and border-radius values because \u2014 unlike index.html \u2014 our renderer
   does NOT overscan the canvas in light mode, so there is no 1-px gap
   between inner element and shader to compensate for. */
.metal-fx-root[data-theme='light'][data-variant='circle'][data-shape='pill'] .metal-fx-inner,
.metal-fx-root[data-theme='light'][data-variant='circle'][data-shape='circle'] .metal-fx-inner {
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0);
}

/* \u2500\u2500\u2500 Combined glow SVG (z=3) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
   Single SVG per instance that holds BOTH the wide-halo group
   (#mfx_haloTravel) and the catch-light group (#mfx_extraTravel), exactly
   mirroring canonical's _buildGlowSvgInner (index.html L8078). One
   mix-blend-mode: screen lifts the combined composite onto the shader
   ring; per-frame opacity attributes on each inner group still drive the
   independent fade-in / fade-out cycles for the halo and the catch-light.

   Why a single SVG: the circle variant anchors halo + catch-light at the same
   perimeter point, so they overlap in the bright zone. Two separately-
   screened SVGs would double-screen the overlap (A + B + C - AB - AC -
   BC + ABC instead of A + B + C - AB - AC once both groups composite
   in source-over inside one SVG and then screen against the host once).
   That overlap looked muted versus canonical specifically on the circle
   variant where both layers travel together.

   Source-of-truth opacity: #btnGlowSvg drops to 0.7 in dark and 0.2746 in
   light (index.html L632/L643). */
.metal-fx-glow-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
  z-index: 3;
  pointer-events: none;
  opacity: 0.7;
}
.metal-fx-root[data-theme='light'] .metal-fx-glow-svg {
  /* Light-mode 1-px overscan mirrors .btn-glow-svg in metal.html so the
     halo stays glued to the visible silhouette (the shader ring there sits
     1 px outside the host's padding box). */
  inset: -1px;
  width: calc(100% + 2px);
  height: calc(100% + 2px);
  mix-blend-mode: multiply;
  /* Source-of-truth: html[data-theme="light"] #btnGlowSvg { opacity: 0.2746 }
     \u2192 \u221235 % from 0.4225 from the original 0.7 dark-mode opacity. */
  opacity: 0.2746;
  filter: saturate(5.355) brightness(0.78);
}
/* Circle light-mode small variants (e.g. 36\xD736 send button): the geometrically
   shrunk halo loses density when multiplied against #ffffff. Mirror the
   canonical override at index.html L2316 \u2014 bump saturation + drop brightness
   so the small glow holds together visually. */
.metal-fx-root[data-variant='circle'][data-shape='circle'][data-theme='light'] .metal-fx-glow-svg {
  filter: saturate(7.5) brightness(0.6);
}

/* The wrapped child \u2014 hoisted into z=5 so it sits above every overlay, with
   normalized chrome so consumer button styles don't fight the metal frame. */
.metal-fx-content {
  position: relative;
  z-index: 5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  pointer-events: none;
}
.metal-fx-content > * {
  pointer-events: auto;
}
.metal-fx-root[data-normalize='true'] .metal-fx-content > * {
  background: transparent !important;
  border: 0 !important;
  outline: 0 !important;
  box-shadow: none !important;
  /* Sizing: we deliberately DO NOT force \`width: 100%; height: 100%\` on the
     child here. That used to be the contract ("the wrapper is the visible
     button surface; the child stretches to fill it"), but it created a cyclic
     percentage dependency: the wrapper is \`inline-flex\` with no intrinsic
     size, .metal-fx-content is \`width/height: 100%\` of the wrapper, and the
     child was \`100%\` of .metal-fx-content. With nothing breaking the cycle,
     icon-only / class-sized children collapsed.

     The new contract: the child sizes itself (intrinsic content, CSS class,
     or inline style \u2014 all work), and the wrapper's \`inline-flex\` wraps it
     tightly. Consumers who want a metal frame BIGGER than the child (e.g.
     padding around an icon) size <MetalFx style={{ width, height }}> AND
     explicitly set width/height on the child to fill (or accept that the
     child renders at its intrinsic size, centered).

     Typography is intentionally NOT touched. We used to apply
     \`color: inherit; font: inherit;\` here to "match" the wrapper, but
     \`font: inherit\` is a shorthand that overrides font-family, font-size,
     font-weight, AND line-height on the child \u2014 which (a) shrank the
     button height (line-height changes propagate through the flex
     content box) and (b) scaled em-based icons / font-icons inside the
     child to whatever the wrapper inherited. The wrapper now stays out
     of the child's typography entirely; consumers who want typographic
     normalization can apply it themselves on the child element. */
}

[data-metal-fx-reflection] {
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  overflow: hidden;
  z-index: 0;
  isolation: isolate;
}
.metal-fx-reflection-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  filter: blur(4px) saturate(1.2) brightness(1.58);
}
.metal-fx-reflection-stroke-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  filter: saturate(1.35) brightness(1.75);
}
/* Hosts that participate as reflection targets need positioning + isolation
   so the wrap composites only against the host (not the parent stack). The
   wrap injects these inline as well, but stating them here keeps reflections
   working on hosts that already have other inline styles applied. */
[data-metal-fx-reflect-host] {
  isolation: isolate;
}
`,Dt=!1;function ni(){if(Dt||typeof document>"u")return;if(document.getElementById(en)){Dt=!0;return}let e=document.createElement("style");e.id=en,e.textContent=oi,document.head.appendChild(e),Dt=!0}ni();var ai={position:"absolute",inset:0,width:"100%",height:"100%"},ri={position:"absolute",inset:3},ii={position:"absolute",inset:0,pointerEvents:"none",zIndex:3,borderRadius:"inherit"},si={position:"absolute",inset:0,pointerEvents:"none",zIndex:4},ot=new Map;function li(){let e=globalThis;e.__MFX_DEBUG__&&(e.__mfxGlow=ot)}Ba((e,t)=>{let n=ot.get(e);return n?br(n.handles,e,t,e.opacityMul*e.glowGain,n.themeRef.current):!1});function ci(e){let[t,n]=(0,z.useState)(()=>e!=="auto"?e:typeof window>"u"||!window.matchMedia||window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");return(0,z.useEffect)(()=>{if(e!=="auto"){n(e);return}if(typeof window>"u"||!window.matchMedia)return;let a=window.matchMedia("(prefers-color-scheme: dark)"),o=()=>n(a.matches?"dark":"light");return o(),a.addEventListener("change",o),()=>a.removeEventListener("change",o)},[e]),t}var Nn=(0,z.forwardRef)(function({children:e,variant:t="button",preset:n="chromatic",theme:a="auto",strength:o=1,glowGain:i=1,paused:r=!1,borderRadius:l,normalizeHostStyles:s=!0,reflectionTargets:c,disableGlow:u=!1,innerShadow:d,shaderScale:m,ringCssPx:p,scale:g=1,mask:f,glowMode:y="mask",className:b,style:v,...h},M){let w=(0,z.useRef)(null),E=(0,z.useRef)(null),F=(0,z.useRef)(null),L=(0,z.useRef)(null),A=(0,z.useRef)(null),Y=(0,z.useRef)(null),P=(0,z.useRef)(null),$=(0,z.useRef)(null),C=(0,z.useRef)("dark"),V=(0,z.useRef)(0),[q,W]=(0,z.useState)(!1),k=ci(a),_=(0,z.useMemo)(()=>Rt(),[]);C.current=k;let R=t==="circle"?"circle":"pill",J=!u;(0,z.useImperativeHandle)(M,()=>w.current,[]);let Q=(I,O)=>{if(R==="circle")return Math.min(I,O)/2;let D=typeof l=="number"?l:(()=>{var U;let N=(U=Y.current)==null?void 0:U.firstElementChild;if(N){let re=parseFloat(getComputedStyle(N).borderTopLeftRadius);if(Number.isFinite(re)&&re>0)return re}return V.current})();return Math.min(D,Math.min(I,O)/2)};(0,z.useEffect)(()=>{_&&Oa(n,k)},[n,k,_]),(0,z.useEffect)(()=>{let I=P.current;I&&Ne(I,{mask:f??null})},[f]),(0,z.useEffect)(()=>{let I=P.current;I&&Ne(I,{paused:r})},[r]),(0,z.useEffect)(()=>{let I=P.current;if(!I)return;let O={};m!==void 0&&(O.shaderScale=m),p!==void 0&&(O.ringCssPx=p),g!==void 0&&(O.scale=g),Object.keys(O).length>0&&Ne(I,O)},[m,p,g]),(0,z.useLayoutEffect)(()=>{let I=E.current,O=w.current,D=F.current;if(!I||!O||!_)return;{let T=getComputedStyle(O),H=parseFloat(T.borderTopLeftRadius);V.current=Number.isFinite(H)?H:0}let U=()=>{let T=O.getBoundingClientRect(),H=Math.max(1,Math.round(T.width)),K=Math.max(1,Math.round(T.height));return{cssWidth:H,cssHeight:K,cornerRadius:Q(H,K)}},N=U();P.current=Ca({onComposite:()=>{let T=P.current,H=$.current;T&&H&&wr(H,T.deform);let K=A.current;T&&K&&An(K,T.deform)},hostCanvas:I,cssWidth:N.cssWidth,cssHeight:N.cssHeight,cornerRadius:N.cornerRadius,kind:R,paused:r,shaderScale:m,ringCssPx:p,scale:g,mask:f??null,onFirstCopy:()=>W(!0)}),O.style.setProperty("--mfx-radius",`${N.cornerRadius}px`),O.style.borderRadius=`${N.cornerRadius}px`;let re=(T,H)=>{if(!f||y==="ring")return{};let K=window.devicePixelRatio||1,ue=document.createElement("canvas");ue.width=Math.max(1,Math.round(T*K)),ue.height=Math.max(1,Math.round(H*K));let ut=ue.getContext("2d");if(!ut)return{};ut.fillStyle="#fff",f(ut,ue.width,ue.height,K);let Hn=ut.getImageData(0,0,ue.width,ue.height).data,co=[],dt=Math.max(1,Math.round(2*K));for(let ht=dt>>1;ht<ue.height;ht+=dt)for(let mt=dt>>1;mt<ue.width;mt+=dt)Hn[(ht*ue.width+mt)*4+3]>128&&co.push({x:mt/K,y:ht/K});return{samplePoints:co,maskDataUrl:ue.toDataURL("image/png")}};D&&($.current=zo(D,{width:N.cssWidth,height:N.cssHeight,cornerRadius:N.cornerRadius,kind:R,scale:g,...re(N.cssWidth,N.cssHeight)}));let ne=T=>{if(!D)return;let H=$.current;D.innerHTML="",$.current=zo(D,{width:T.cssWidth,height:T.cssHeight,cornerRadius:T.cornerRadius,kind:R,scale:g,...re(T.cssWidth,T.cssHeight)}),H&&Mr(H,$.current);let K=P.current;K&&$.current&&ot.set(K,{handles:$.current,themeRef:C})},ae=()=>d?d===!0?$o:{...$o,...d}:null,oe=T=>{let H=L.current,K=P.current;Go(A.current),A.current=null;let ue=ae();!H||!K||!ue||(A.current=_r(H,{width:T.cssWidth,height:T.cssHeight,cornerRadius:T.cornerRadius,kind:R,ring:K.ringCssPx},ue))};oe(N);let ie=0,ce=N.cssWidth,se=N.cssHeight,B=N.cornerRadius,j=new ResizeObserver(()=>{ie===0&&(ie=requestAnimationFrame(()=>{ie=0;let T=U(),H=P.current;!H||Math.abs(T.cssWidth-ce)<.5&&Math.abs(T.cssHeight-se)<.5&&Math.abs(T.cornerRadius-B)<.5||(ce=T.cssWidth,se=T.cssHeight,B=T.cornerRadius,Ne(H,{cssWidth:T.cssWidth,cssHeight:T.cssHeight,cornerRadius:T.cornerRadius}),O.style.setProperty("--mfx-radius",`${T.cornerRadius}px`),O.style.borderRadius=`${T.cornerRadius}px`,ne(T),oe(T))}))});j.observe(O);let X=null,le=()=>{let T=P.current;if(T&&Aa(T)){let H=U();ne(H),oe(H)}qe()},qe=()=>{X?.removeEventListener("change",le),X=typeof window.matchMedia=="function"?window.matchMedia(`(resolution: ${window.devicePixelRatio||1}dppx)`):null,X?.addEventListener("change",le)};qe();let ct=Ua(T=>{T&&P.current&&ne(U())}),Me=null;return typeof IntersectionObserver<"u"&&(Me=new IntersectionObserver(T=>{let H=P.current;if(H)for(let K of T)Ea(H,K.isIntersecting)},{rootMargin:"64px"}),Me.observe(O)),P.current&&$.current&&(ot.set(P.current,{handles:$.current,themeRef:C}),ka(P.current)),Ga(),li(),()=>{Wa(),Go(A.current),A.current=null,j.disconnect(),X?.removeEventListener("change",le),Me?.disconnect(),ct(),ie!==0&&cancelAnimationFrame(ie);let T=P.current;T&&(ot.delete(T),Ta(T),Ra(T)),P.current=null,$.current=null,D&&(D.innerHTML="")}},[R]),(0,z.useEffect)(()=>{let I=P.current;I&&Ne(I,{opacityMul:Math.max(0,Math.min(1,o)),glowGain:Math.max(0,i)})},[o,i,t]),(0,z.useEffect)(()=>{let I=P.current,O=w.current;if(!I||!O||!c||k!=="dark")return;I.onAfterFrame=ti;let D=c.flatMap(U=>{let N="current"in U?U:U.ref,re="current"in U?1:U.strength??1;return N.current?[{el:N.current,strength:re}]:[]});for(let{el:U,strength:N}of D)Kr(U,I,O,N);return()=>{I.onAfterFrame=void 0;for(let{el:U}of D)Zr(U)}},[c,k]),(0,z.useEffect)(()=>{let I=w.current,O=P.current;if(!I||!O)return;let D=Q(O.cssWidth,O.cssHeight);Ne(O,{cornerRadius:D}),I.style.setProperty("--mfx-radius",`${D}px`),I.style.borderRadius=`${D}px`},[l,k,t,R]);let te=(0,z.useMemo)(()=>({...v,"--mfx-strength":String(Math.min(1,Math.max(0,o))),opacity:q?1:0,visibility:q?"visible":"hidden",transition:q?"opacity 0.15s ease-out":"none"}),[v,o,q]);return _?mo("div",{...h,ref:w,className:b?`metal-fx-root ${b}`:"metal-fx-root","data-variant":t,"data-shape":R,"data-theme":k,"data-paused":r?"true":void 0,"data-normalize":s?"true":"false",style:te,children:[ge("canvas",{ref:E,className:"metal-fx-canvas",style:ai}),ge("div",{className:"metal-fx-inner","aria-hidden":"true",style:ri}),ge("div",{ref:F,"aria-hidden":"true",style:{...ii,display:J?void 0:"none"}}),d?ge("div",{ref:L,"aria-hidden":"true",style:si}):null,ge("div",{ref:Y,className:"metal-fx-content",children:e})]}):ge("div",{...h,ref:w,className:b?`metal-fx-fallback ${b}`:"metal-fx-fallback","data-metal-fx-unsupported":"",style:{display:"inline-flex",...v},children:e})});Nn.displayName="MetalFx";function Un(e,t,n,a){let o=getComputedStyle(n),i=t.getBoundingClientRect(),r=document.createRange();r.selectNodeContents(n);let l=r.getBoundingClientRect();r.detach(),e.save(),e.scale(a,a),e.font=`${o.fontStyle} ${o.fontWeight} ${o.fontSize} ${o.fontFamily}`,e.textAlign="left",e.textBaseline="alphabetic";let s=n.textContent??"",c=e.measureText(s),u=c.fontBoundingBoxAscent??parseFloat(o.fontSize)*.9,d=c.fontBoundingBoxDescent??parseFloat(o.fontSize)*.2,m=l.left-i.left,p=l.top-i.top+(l.height-(u+d))/2+u;e.fillText(s,m,p),e.restore()}var zn={offsetY:1,blur:.5,alpha:.9},$t=Object.freeze({metalOpacity:.62,shaderScale:2.8,glowGain:2.5,innerShadow:zn});function ui(e,t,n,a){let o=window.devicePixelRatio||1,i=t.getBoundingClientRect(),r=Math.max(1,Math.round(i.width*o)),l=Math.max(1,Math.round(i.height*o)),s=document.createElement("canvas");s.width=r,s.height=l;let c=s.getContext("2d",{willReadFrequently:!0}),u=e.getContext("2d");if(!c||!u)return;c.fillStyle="#fff",Un(c,t,n,o);let d=c.getImageData(0,0,r,l).data,m=r*l,p=new Float32Array(m);for(let h=0,M=3;h<m;h++,M+=4)p[h]=d[M]/255;let g=Math.max(1,Math.round(a.offsetY*o))*r,f=new Float32Array(m);for(let h=0;h<m;h++){let M=h>=g?p[h-g]:0;f[h]=Math.max(0,p[h]-M)}let y=Tt(f,r,l,a.blur*o);e.width=r,e.height=l,e.style.width=`${i.width}px`,e.style.height=`${i.height}px`;let b=u.createImageData(r,l),v=b.data;for(let h=0,M=0;h<m;h++,M+=4)v[M]=255,v[M+1]=255,v[M+2]=255,v[M+3]=Math.round(Math.min(1,y[h]*p[h]*a.alpha)*255);u.putImageData(b,0,0)}var tn="mfx-bare-style",di=".metal-fx-root[data-mfx-bare]{background:transparent!important}.metal-fx-root[data-mfx-bare]::before,.metal-fx-root[data-mfx-bare]::after{box-shadow:none!important}.metal-fx-root[data-mfx-bare] .metal-fx-inner{display:none!important}";function Dn({children:e,font:t,color:n,strength:a=1,theme:o,reflectionTargets:i,className:r,innerShadow:l=zn,glow:s=!1,glowGain:c=$t.glowGain,metalOpacity:u=$t.metalOpacity,shaderScale:d=$t.shaderScale}){let m=(0,z.useRef)(null),p=(0,z.useRef)(null);(0,z.useEffect)(()=>{var y,b,v,h;if(!document.getElementById(tn)){let E=document.createElement("style");E.id=tn,E.textContent=di,document.head.appendChild(E)}(y=m.current)==null||y.setAttribute("data-mfx-bare","");let M=(b=m.current)==null?void 0:b.querySelector("canvas.metal-fx-canvas");M&&(M.style.zIndex="6");let w=(h=(v=m.current)==null?void 0:v.querySelector(".metal-fx-glow-svg"))==null?void 0:h.parentElement;w&&(w.style.zIndex="7")},[]),(0,z.useEffect)(()=>{var y;let b=m.current,v=p.current;if(!b||!v||!l)return;let h=document.createElement("canvas");h.className="metal-fx-text-rim",h.setAttribute("aria-hidden","true"),h.style.cssText="position:absolute;left:0;top:0;pointer-events:none;z-index:8",b.appendChild(h);let M=()=>ui(h,b,v,l);M();let w=!0;(y=document.fonts)==null||y.ready.then(()=>{w&&M()});let E=new ResizeObserver(M);E.observe(b);let F=null,L=()=>{F?.removeEventListener("change",A),F=typeof window.matchMedia=="function"?window.matchMedia(`(resolution: ${window.devicePixelRatio||1}dppx)`):null,F?.addEventListener("change",A)},A=()=>{w&&(M(),L())};return L(),()=>{w=!1,E.disconnect(),F?.removeEventListener("change",A),h.remove()}},[l]);let g=(0,z.useCallback)((y,b,v,h)=>{let M=m.current,w=p.current;M&&w&&Un(y,M,w,h)},[]),f={font:t,color:n,letterSpacing:0,whiteSpace:"nowrap"};return ge(Nn,{ref:m,preset:"chromatic",theme:o,strength:a*u,glowGain:c,disableGlow:!s,mask:g,reflectionTargets:i,shaderScale:d,borderRadius:4,style:{background:"transparent",borderRadius:4},children:ge("span",{ref:p,className:r,style:f,"aria-label":e,children:e})})}var hi=45;var mi=26.667,yi=(hi-mi)/2;var Mi=Object.freeze({metalOpacity:.8,shaderScale:1.6,core:Object.freeze({r:46,blur:100,a:.94,size:49}),gradient:0,glow:.41});var fi=Object.freeze({enabled:!0,applyTo:"ring",strength:.74,fadeInMs:200,fadeOutMs:350,smoothMs:140,reach:36,blob:13,liquidBlob:10,maxDisp:9,gain:.6,pressGain:.55,pullGain:.49,press:5,liquid:7.5,liquidReach:8,liquidStiffness:53,liquidDamping:9,stiffness:260,damping:13,mass:1,follow:.32,mapRes:2,smooth:.25}),_i={...fi};var lo=window.React,Gn=lo.createElement;Rt()&&hn({...Ct.chromatic.modes.dark,speed:.7,colorTint:"#b8d7ff40",shiftRed:.65,shiftBlue:.7,softness:.12});var $n=()=>document.documentElement.getAttribute("data-theme")==="light"?"light":"dark";function pi({text:e}){let[t,n]=lo.useState($n());return lo.useEffect(()=>{let a=new MutationObserver(()=>n($n()));return a.observe(document.documentElement,{attributes:!0,attributeFilter:["data-theme"]}),()=>a.disconnect()},[]),Gn(Dn,{font:"inherit",color:t==="light"?"#8594a4":"#c6d3e6",theme:t,strength:1,metalOpacity:1,shaderScale:2.2,innerShadow:null,className:"dsx-metal-glyphs"},e)}function Wn(e=document){!Rt()||window.matchMedia("(prefers-reduced-motion: reduce)").matches||e.querySelectorAll("[data-metal-text]:not([data-metal-mounted])").forEach(t=>{t.setAttribute("data-metal-mounted","");let n=t.textContent;t.textContent="",t.style.letterSpacing="0",window.DSXMetal.createRoot(t).render(Gn(pi,{text:n}))})}window.DSXMetalText={mount:Wn};var Vn=()=>(document.fonts?document.fonts.ready:Promise.resolve()).then(()=>Wn());document.readyState==="loading"?document.addEventListener("DOMContentLoaded",Vn):Vn();})();
