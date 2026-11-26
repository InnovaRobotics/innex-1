const SANS = "'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif";

function roverTopDownSvg(x, y, deg, stroke, fill) {
  return `
    <g transform="translate(${x}, ${y}) rotate(${deg})">
      <rect x="-20" y="-13" width="40" height="26" rx="2" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
      <!-- Six paddle wheels -->
      <rect x="-18" y="-17" width="9" height="3.5" rx="1" fill="${stroke}"/>
      <rect x="-4.5" y="-17" width="9" height="3.5" rx="1" fill="${stroke}"/>
      <rect x="9" y="-17" width="9" height="3.5" rx="1" fill="${stroke}"/>
      <rect x="-18" y="13.5" width="9" height="3.5" rx="1" fill="${stroke}"/>
      <rect x="-4.5" y="13.5" width="9" height="3.5" rx="1" fill="${stroke}"/>
      <rect x="9" y="13.5" width="9" height="3.5" rx="1" fill="${stroke}"/>
      <!-- Forward heading arrow -->
      <line x1="-2" y1="0" x2="12" y2="0" stroke="${stroke}" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M 8 -3.5 L 13 0 L 8 3.5" fill="none" stroke="${stroke}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </g>`;
}

export function renderIcpWallDiagram() {
  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 264" role="img" aria-label="Two-step comparison of LiDAR wall scan matching: on the left, two consecutive scans of an arena corner appear shifted; on the right, aligning the rigid corner walls reveals the rover's forward motion and turn.">
      <defs>
        <pattern id="grid-24" width="24" height="24" patternUnits="userSpaceOnUse">
          <path d="M 24 0 L 0 0 0 24" fill="none" stroke="rgba(255,255,255,0.035)" stroke-width="1"/>
        </pattern>
        <marker id="icp-arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>

      <!-- Panel 1: Before alignment -->
      <text x="16" y="20" fill="#eceef2" font-family="${SANS}" font-size="13" font-weight="500">1. Two scans 100 ms apart</text>
      <rect x="16" y="30" width="320" height="216" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.1)"/>
      <rect x="16" y="30" width="320" height="216" fill="url(#grid-24)"/>

      <!-- Previous wall corner (dashed grey) -->
      <path d="M 52 212 L 52 68 L 284 68" fill="none" stroke="#8e95a2" stroke-width="1.5" stroke-dasharray="5 4"/>
      <!-- Current wall corner seen from moved rover (shifted & rotated before alignment) -->
      <g transform="translate(-22, 12) rotate(-7 176 148)">
        <path d="M 52 212 L 52 68 L 284 68" fill="none" stroke="#4f7bd9" stroke-width="1.8"/>
        <circle cx="52" cy="186" r="2.3" fill="#4f7bd9"/>
        <circle cx="52" cy="148" r="2.3" fill="#4f7bd9"/>
        <circle cx="52" cy="110" r="2.3" fill="#4f7bd9"/>
        <circle cx="52" cy="72" r="2.3" fill="#4f7bd9"/>
        <circle cx="96" cy="68" r="2.3" fill="#4f7bd9"/>
        <circle cx="144" cy="68" r="2.3" fill="#4f7bd9"/>
        <circle cx="192" cy="68" r="2.3" fill="#4f7bd9"/>
        <circle cx="240" cy="68" r="2.3" fill="#4f7bd9"/>
      </g>

      ${roverTopDownSvg(176, 166, -12, "#b2b8c2", "#14171c")}

      <text x="64" y="54" fill="#8e95a2" font-family="${SANS}" font-size="12">Previous wall scan</text>
      <text x="150" y="96" fill="#7098ec" font-family="${SANS}" font-size="12">New scan appears shifted</text>

      <!-- Panel 2: After ICP alignment -->
      <text x="364" y="20" fill="#eceef2" font-family="${SANS}" font-size="13" font-weight="500">2. Slide and rotate until walls match</text>
      <rect x="364" y="30" width="320" height="216" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.1)"/>
      <rect x="364" y="30" width="320" height="216" fill="url(#grid-24)"/>

      <!-- Rigid arena corner with both scans locked together -->
      <path d="M 400 212 L 400 68 L 636 68" fill="none" stroke="#eceef2" stroke-width="2"/>
      <g fill="#4f7bd9">
        <circle cx="400" cy="186" r="2.5"/>
        <circle cx="400" cy="148" r="2.5"/>
        <circle cx="400" cy="110" r="2.5"/>
        <circle cx="400" cy="72" r="2.5"/>
        <circle cx="444" cy="68" r="2.5"/>
        <circle cx="492" cy="68" r="2.5"/>
        <circle cx="540" cy="68" r="2.5"/>
        <circle cx="588" cy="68" r="2.5"/>
      </g>
      <text x="412" y="54" fill="#b2b8c2" font-family="${SANS}" font-size="12">Rigid arena corner (scans aligned)</text>

      <!-- Ghost previous rover + aligned new rover + motion arrow -->
      <g opacity="0.45">
        ${roverTopDownSvg(498, 178, -12, "#8e95a2", "none")}
      </g>
      <line x1="518" y1="172" x2="554" y2="156" stroke="#4f7bd9" stroke-width="1.8" marker-end="url(#icp-arrow-blue)"/>
      ${roverTopDownSvg(582, 144, -5, "#4f7bd9", "rgba(79,123,217,0.16)")}

      <text x="538" y="206" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="12.5" font-weight="500">True rover motion recovered</text>
      <text x="538" y="224" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Independent of wheel slip on sand</text>
    </svg>
  </div>
  <figcaption class="figure-caption">
    Aligning consecutive 3D LiDAR scans against the rigid arena walls recovers how far the rover moved and turned over that interval, even when the tyres slip in loose sand.
  </figcaption>
</figure>`;
}

export function renderRep105Diagram() {
  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 286" role="img" aria-label="Comparison between a single coordinate frame, where a 25 cm beacon update creates a sharp jump into a boulder, and the REP 105 map-to-odom-to-base_link split, where local steering stays smooth while map-to-odom shifts the arena origin.">
      <defs>
        <marker id="rep-arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="rep-arrow-muted" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#b2b8c2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>

      <!-- Left panel: Single frame problem -->
      <text x="16" y="20" fill="#eceef2" font-family="${SANS}" font-size="13" font-weight="500">Single frame: beacon fix causes a steering jump</text>
      <rect x="16" y="30" width="320" height="172" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.1)"/>

      <!-- Smooth path until mid-turn snap -->
      <path d="M 42 156 C 92 156, 126 88, 174 84" fill="none" stroke="#b2b8c2" stroke-width="1.6"/>
      <!-- Instantaneous 25 cm snap downward + overcorrection into boulder -->
      <line x1="174" y1="84" x2="174" y2="118" stroke="#eceef2" stroke-width="1.5" stroke-dasharray="3 3" marker-end="url(#rep-arrow-muted)"/>
      <path d="M 174 118 C 194 136, 206 144, 220 148" fill="none" stroke="#eceef2" stroke-width="1.6"/>

      <!-- Boulder -->
      <circle cx="238" cy="152" r="20" fill="#181c22" stroke="#8e95a2" stroke-width="1.4"/>
      <text x="238" y="188" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Boulder</text>

      <text x="184" y="102" fill="#eceef2" font-family="${SANS}" font-size="11.5">25 cm snap</text>
      <text x="42" y="54" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Controller reacts to sudden step error</text>

      <!-- Right panel: REP 105 two-frame solution -->
      <text x="364" y="20" fill="#eceef2" font-family="${SANS}" font-size="13" font-weight="500">REP 105 split: local steering stays smooth</text>
      <rect x="364" y="30" width="320" height="172" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.1)"/>

      <!-- Drifted local odom path (dashed) -->
      <path d="M 392 132 C 446 132, 488 76, 558 76 C 602 76, 632 88, 660 92" fill="none" stroke="#8e95a2" stroke-width="1.3" stroke-dasharray="5 4"/>
      <!-- True arena path after map -> odom shift (blue) -->
      <path d="M 392 164 C 446 164, 488 108, 558 108 C 602 108, 632 120, 660 124" fill="none" stroke="#4f7bd9" stroke-width="2"/>

      <!-- Origin shift indicator on left -->
      <line x1="392" y1="134" x2="392" y2="158" stroke="#4f7bd9" stroke-width="1.6" marker-end="url(#rep-arrow-blue)"/>
      <text x="386" y="188" fill="#7098ec" font-family="${SANS}" font-size="11.5">Origin shifts 25 cm</text>

      <!-- Boulder -->
      <circle cx="584" cy="154" r="20" fill="#181c22" stroke="#8e95a2" stroke-width="1.4"/>
      <text x="584" y="188" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Boulder cleared</text>

      <text x="390" y="54" fill="#8e95a2" font-family="${SANS}" font-size="11.5">No step jump seen by wheel controller</text>

      <!-- Bottom chain summary -->
      <rect x="16" y="218" width="164" height="54" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.14)"/>
      <text x="30" y="241" fill="#eceef2" font-family="${SANS}" font-size="13" font-weight="600">map</text>
      <text x="30" y="259" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Fixed to arena</text>

      <line x1="180" y1="245" x2="264" y2="245" stroke="#4f7bd9" stroke-width="1.75" marker-end="url(#rep-arrow-blue)"/>
      <text x="222" y="235" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">Beacon fix</text>
      <text x="222" y="262" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11">can jump</text>

      <rect x="268" y="218" width="164" height="54" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.14)"/>
      <text x="282" y="241" fill="#eceef2" font-family="${SANS}" font-size="13" font-weight="600">odom</text>
      <text x="282" y="259" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Smooth local origin</text>

      <line x1="432" y1="245" x2="516" y2="245" stroke="#b2b8c2" stroke-width="1.5" marker-end="url(#rep-arrow-muted)"/>
      <text x="474" y="235" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="11.5">Odometry</text>
      <text x="474" y="262" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11">continuous</text>

      <rect x="520" y="218" width="164" height="54" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.14)"/>
      <text x="534" y="241" fill="#eceef2" font-family="${SANS}" font-size="13" font-weight="600">base_link</text>
      <text x="534" y="259" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Rover body</text>
    </svg>
  </div>
  <figcaption class="figure-caption">
    Placing <code>odom</code> between <code>map</code> and <code>base_link</code> lets discrete beacon updates correct arena drift in <code>map → odom</code> while short-range controllers steer on the continuous <code>odom → base_link</code> transform.
  </figcaption>
</figure>`;
}

export function renderKalmanMathBlock1() {
  return `
<div class="math-block" role="math" aria-label="weight equals prediction variance divided by prediction variance plus measurement variance">
  <div class="math-row">
    <span>weight =</span>
    <span class="math-frac">
      <span class="math-num">prediction variance</span>
      <span class="math-den">prediction variance + measurement variance</span>
    </span>
  </div>
</div>`;
}

export function renderKalmanMathBlock2() {
  return `
<div class="math-block" role="math" aria-label="weight equals 0.09 divided by 0.09 plus 0.01 equals 0.90; updated position equals 2.00 plus 0.90 times negative 0.40 equals 1.64 metres">
  <div class="math-row">
    <span>weight =</span>
    <span class="math-frac">
      <span class="math-num">0.09</span>
      <span class="math-den">0.09 + 0.01</span>
    </span>
    <span>= <span class="math-accent">0.90</span></span>
  </div>
  <div class="math-row">
    <span>updated position = 2.00 + 0.90 × (1.60 − 2.00) = <span class="math-accent">1.64 m</span></span>
  </div>
</div>`;
}

export function renderInteractiveKalmanFigure() {
  return `
<figure class="tech-figure" id="kalman-explorer">
  <div class="figure-frame">
    <svg id="kalman-svg" viewBox="0 0 700 228" role="img" aria-label="Interactive probability curves comparing wheel odometry at 2.00 m, beacon sighting at 1.60 m, and the variance-weighted Kalman estimate.">
      <!-- Baseline and evenly spaced axis labels in body sans -->
      <line x1="36" y1="188" x2="664" y2="188" stroke="rgba(255,255,255,0.18)" stroke-width="1"/>
      <g fill="#8e95a2" font-family="${SANS}" font-size="12" text-anchor="middle">
        <line x1="80" y1="188" x2="80" y2="194" stroke="rgba(255,255,255,0.18)"/>
        <text x="80" y="212">1.2 m</text>
        <line x1="226" y1="188" x2="226" y2="194" stroke="rgba(255,255,255,0.34)"/>
        <text x="226" y="212" fill="#eceef2">1.6 m (beacon)</text>
        <line x1="372" y1="188" x2="372" y2="194" stroke="rgba(255,255,255,0.34)"/>
        <text x="372" y="212" fill="#b2b8c2">2.0 m (wheels)</text>
        <line x1="518" y1="188" x2="518" y2="194" stroke="rgba(255,255,255,0.18)"/>
        <text x="518" y="212">2.4 m</text>
        <line x1="628" y1="188" x2="628" y2="194" stroke="rgba(255,255,255,0.18)"/>
        <text x="628" y="212">2.7 m</text>
      </g>

      <!-- Legend -->
      <g font-family="${SANS}" font-size="12">
        <line x1="464" y1="22" x2="488" y2="22" stroke="#8e95a2" stroke-width="1.5"/>
        <text x="496" y="26" fill="#b2b8c2">Wheel prediction</text>
        <line x1="464" y1="42" x2="488" y2="42" stroke="#eceef2" stroke-width="1.4" stroke-dasharray="4 3"/>
        <text x="496" y="46" fill="#eceef2">Beacon measurement</text>
        <line x1="464" y1="62" x2="488" y2="62" stroke="#4f7bd9" stroke-width="2"/>
        <text x="496" y="66" fill="#7098ec" font-weight="500">Fused estimate</text>
      </g>

      <!-- Dynamic curves -->
      <path id="curve-pred" fill="none" stroke="#8e95a2" stroke-width="1.5" d=""/>
      <path id="curve-meas" fill="none" stroke="#eceef2" stroke-width="1.4" stroke-dasharray="4 3" d=""/>
      <path id="curve-fused-fill" fill="rgba(79,123,217,0.14)" stroke="none" d=""/>
      <path id="curve-fused" fill="none" stroke="#4f7bd9" stroke-width="2.1" d=""/>
      <line id="line-fused-mean" x1="241" y1="24" x2="241" y2="188" stroke="#4f7bd9" stroke-width="1" stroke-dasharray="3 3"/>
    </svg>

    <div class="kalman-metrics" role="status" aria-live="polite">
      <div class="metric-cell">
        <span class="metric-name">Wheel variance</span>
        <span class="metric-val" id="out-p">0.090 m²</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Beacon variance</span>
        <span class="metric-val" id="out-r">0.010 m²</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Kalman gain</span>
        <span class="metric-val is-accent" id="out-k">0.90</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Fused position</span>
        <span class="metric-val is-accent" id="out-x">1.64 m (±0.09 m)</span>
      </div>
    </div>

    <div class="kalman-controls">
      <div class="slider-field">
        <div class="slider-label-row">
          <label for="slider-pred">Wheel typical error</label>
          <span class="slider-readout" id="label-pred">0.30 m</span>
        </div>
        <input id="slider-pred" type="range" min="0.05" max="0.60" step="0.01" value="0.30"/>
      </div>
      <div class="slider-field">
        <div class="slider-label-row">
          <label for="slider-meas">Beacon typical error</label>
          <span class="slider-readout" id="label-meas">0.10 m</span>
        </div>
        <input id="slider-meas" class="accent-slider" type="range" min="0.02" max="3.00" step="0.01" value="0.10"/>
      </div>
    </div>

    <div class="preset-bar" role="group" aria-label="Sensor uncertainty presets">
      <div class="preset-indicator" id="preset-indicator" aria-hidden="true"></div>
      <button type="button" class="preset-btn" data-pred="0.30" data-meas="0.10" aria-pressed="true">Worked example</button>
      <button type="button" class="preset-btn" data-pred="0.30" data-meas="0.02" aria-pressed="false">Sharp beacon</button>
      <button type="button" class="preset-btn" data-pred="0.30" data-meas="3.00" aria-pressed="false">Blurry far tag</button>
    </div>
  </div>
  <figcaption class="figure-caption">
    Interactive variance blend between wheel odometry at 2.0 m and a beacon sighting at 1.6 m. Switch between presets or drag either slider to see how measurement certainty shifts the Kalman gain.
  </figcaption>
</figure>`;
}

export function renderPositiveNegativeObstaclesDiagram() {
  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 206" role="img" aria-label="Side-profile comparison showing sensor rays reflecting densely off the front face of a 35 cm boulder while skimming over the near rim of a 45 cm crater and leaving an empty shadow.">
      <!-- Ground profile with boulder and recessed crater -->
      <path d="M 28 152 L 210 152 Q 224 102 248 102 Q 272 102 284 152 L 444 152 L 454 146 L 474 186 L 548 186 L 568 152 L 672 152" fill="none" stroke="#eceef2" stroke-width="1.8"/>

      <!-- Sensor origin on rover -->
      <rect x="40" y="96" width="54" height="36" rx="2" fill="rgba(79,123,217,0.15)" stroke="#4f7bd9" stroke-width="1.5"/>
      <circle cx="94" cy="106" r="3.5" fill="#4f7bd9"/>
      <text x="67" y="86" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12">Sensor</text>

      <!-- Rays hitting positive boulder -->
      <g stroke="#4f7bd9" stroke-width="1.15" opacity="0.85">
        <line x1="94" y1="106" x2="218" y2="132"/>
        <line x1="94" y1="106" x2="225" y2="115"/>
        <line x1="94" y1="106" x2="236" y2="104"/>
      </g>
      <circle cx="218" cy="132" r="2.6" fill="#7098ec"/>
      <circle cx="225" cy="115" r="2.6" fill="#7098ec"/>
      <circle cx="236" cy="104" r="2.6" fill="#7098ec"/>

      <!-- Ray skimming crater lip and missing interior -->
      <line x1="94" y1="106" x2="454" y2="146" stroke="#b2b8c2" stroke-width="1.1" stroke-dasharray="4 3"/>
      <line x1="454" y1="146" x2="624" y2="165" stroke="#8e95a2" stroke-width="1" stroke-dasharray="2 4" opacity="0.55"/>

      <text x="248" y="84" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="12.5" font-weight="500">Boulder (positive obstacle)</text>
      <text x="248" y="174" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Dense cluster of elevated points</text>

      <text x="512" y="128" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">Crater (negative obstacle)</text>
      <text x="512" y="144" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11.5">Near lip hides interior floor</text>
    </svg>
  </div>
  <figcaption class="figure-caption">
    Side-profile ray geometry: a boulder reflects a clear cluster above the sand plane, whereas a crater appears only as a missing-return gap behind its near rim.
  </figcaption>
</figure>`;
}

export function renderMissionCycleDiagram() {
  const steps = [
    { x: 24, label: "1. Localise", sub: "Start zone" },
    { x: 158, label: "2. Traverse", sub: "To excavation" },
    { x: 292, label: "3. Excavate", sub: "Collect sand" },
    { x: 426, label: "4. Return", sub: "To construction" },
    { x: 560, label: "5. Dump", sub: "Build berm" },
  ];
  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 156" role="img" aria-label="Mission cycle flowchart from start-zone localisation through traverse, excavate, return, and dump, with a repeat-or-stop decision based on remaining time and energy.">
      <defs>
        <marker id="mc-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#b2b8c2" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="mc-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>
      ${steps
        .map(
          (s, idx) => `
        <rect x="${s.x}" y="22" width="116" height="52" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.15)"/>
        <text x="${s.x + 12}" y="44" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">${s.label}</text>
        <text x="${s.x + 12}" y="61" fill="#8e95a2" font-family="${SANS}" font-size="11">${s.sub}</text>
        ${
          idx < steps.length - 1
            ? `<line x1="${s.x + 116}" y1="48" x2="${steps[idx + 1].x - 4}" y2="48" stroke="#b2b8c2" stroke-width="1.4" marker-end="url(#mc-arrow)"/>`
            : ""
        }`
        )
        .join("")}
      <!-- Loop back from Dump to Traverse -->
      <path d="M 618 74 L 618 118 L 216 118 L 216 78" fill="none" stroke="#4f7bd9" stroke-width="1.6" marker-end="url(#mc-blue)"/>
      <rect x="314" y="106" width="212" height="22" fill="#101215"/>
      <text x="420" y="121" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">Repeat if time and energy favour another pass</text>
    </svg>
  </div>
  <figcaption class="figure-caption">
    After each dump, the mission layer weighs remaining clock time and accumulated energy before either starting another traverse or stopping cleanly.
  </figcaption>
</figure>`;
}

export function renderHardwareConnectionsDiagram() {
  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 220" role="img" aria-label="Hardware connection diagram from gamepad and mission control laptop through the arena-corner GL-A1300 router to the Jetson Orin Nano Super, sensors, Teensy 4.1, and motor controllers.">
      <defs>
        <marker id="hw-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#b2b8c2" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="hw-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>

      <!-- Mission control & router -->
      <rect x="18" y="84" width="124" height="52" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.15)"/>
      <text x="30" y="106" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">Laptop + gamepad</text>
      <text x="30" y="123" fill="#8e95a2" font-family="${SANS}" font-size="11">Mission control</text>

      <line x1="142" y1="110" x2="188" y2="110" stroke="#b2b8c2" stroke-width="1.4" marker-end="url(#hw-arrow)"/>
      <text x="165" y="101" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Ethernet</text>

      <rect x="192" y="84" width="112" height="52" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.15)"/>
      <text x="204" y="106" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">GL-A1300</text>
      <text x="204" y="123" fill="#8e95a2" font-family="${SANS}" font-size="11">Arena corner</text>

      <line x1="304" y1="110" x2="352" y2="110" stroke="#4f7bd9" stroke-width="1.6" marker-end="url(#hw-blue)"/>
      <text x="328" y="101" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="10.5">Wi-Fi</text>

      <!-- Jetson -->
      <rect x="356" y="84" width="132" height="52" rx="2" fill="rgba(79,123,217,0.12)" stroke="#4f7bd9" stroke-width="1.4"/>
      <text x="368" y="106" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="600">Jetson Orin Nano</text>
      <text x="368" y="123" fill="#b2b8c2" font-family="${SANS}" font-size="11">ROS 2 Jazzy · 25 W</text>

      <!-- Sensors above & below Jetson -->
      <rect x="356" y="14" width="132" height="42" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.14)"/>
      <text x="368" y="33" fill="#eceef2" font-family="${SANS}" font-size="12">Two OAK-D Pro</text>
      <text x="368" y="48" fill="#8e95a2" font-family="${SANS}" font-size="10.5">USB 3 · depth + H.264</text>
      <line x1="422" y1="56" x2="422" y2="80" stroke="#b2b8c2" stroke-width="1.3" marker-end="url(#hw-arrow)"/>

      <rect x="356" y="164" width="132" height="42" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.14)"/>
      <text x="368" y="183" fill="#eceef2" font-family="${SANS}" font-size="12">Ouster OS1-128</text>
      <text x="368" y="198" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Ethernet · LiDAR + IMU</text>
      <line x1="422" y1="164" x2="422" y2="140" stroke="#b2b8c2" stroke-width="1.3" marker-end="url(#hw-arrow)"/>

      <!-- Teensy & motor drivers -->
      <line x1="488" y1="110" x2="536" y2="110" stroke="#4f7bd9" stroke-width="1.6" marker-end="url(#hw-blue)"/>
      <text x="512" y="101" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="10.5">USB</text>

      <rect x="540" y="84" width="142" height="52" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.18)"/>
      <text x="552" y="106" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">Teensy 4.1</text>
      <text x="552" y="123" fill="#8e95a2" font-family="${SANS}" font-size="11">250 ms watchdog</text>

      <line x1="611" y1="136" x2="611" y2="160" stroke="#b2b8c2" stroke-width="1.3" marker-end="url(#hw-arrow)"/>
      <rect x="540" y="164" width="142" height="42" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.14)"/>
      <text x="552" y="183" fill="#eceef2" font-family="${SANS}" font-size="12">Sabertooth + drivers</text>
      <text x="552" y="198" fill="#8e95a2" font-family="${SANS}" font-size="10.5">6 wheels · ladder · bed</text>
    </svg>
  </div>
  <figcaption class="figure-caption">
    Physical link topology: heavy sensing and planning stay on the Jetson, while every motor controller sits behind the Teensy 4.1 hardware watchdog.
  </figcaption>
</figure>`;
}

export function renderSubsystemLoopDiagram() {
  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 204" role="img" aria-label="Closed-loop data flow across Sensors, Perception, Localisation, Navigation and mission, Teleop and control, Comms, and Motors.">
      <defs>
        <marker id="sub-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#b2b8c2" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="sub-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1.5 1.5 L 8.5 5 L 1.5 8.5" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>

      <!-- Sensors -->
      <rect x="20" y="76" width="110" height="48" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.15)"/>
      <text x="75" y="104" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">Sensors</text>

      <!-- Perception & Localisation -->
      <path d="M 130 90 L 184 44" fill="none" stroke="#b2b8c2" stroke-width="1.3" marker-end="url(#sub-arrow)"/>
      <path d="M 130 110 L 184 156" fill="none" stroke="#b2b8c2" stroke-width="1.3" marker-end="url(#sub-arrow)"/>

      <rect x="188" y="20" width="128" height="46" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.15)"/>
      <text x="252" y="47" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">Perception</text>

      <rect x="188" y="136" width="128" height="46" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.15)"/>
      <text x="252" y="163" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">Localisation</text>

      <!-- Navigation -->
      <path d="M 316 44 L 368 88" fill="none" stroke="#b2b8c2" stroke-width="1.3" marker-end="url(#sub-arrow)"/>
      <path d="M 316 156 L 368 112" fill="none" stroke="#b2b8c2" stroke-width="1.3" marker-end="url(#sub-arrow)"/>

      <rect x="372" y="76" width="138" height="48" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.15)"/>
      <text x="441" y="97" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">Navigation &amp;</text>
      <text x="441" y="113" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="500">mission</text>

      <!-- Teleop & Control -->
      <line x1="510" y1="100" x2="552" y2="100" stroke="#4f7bd9" stroke-width="1.6" marker-end="url(#sub-blue)"/>
      <rect x="556" y="76" width="124" height="48" rx="2" fill="rgba(79,123,217,0.12)" stroke="#4f7bd9" stroke-width="1.4"/>
      <text x="618" y="97" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="600">Teleop &amp;</text>
      <text x="618" y="113" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="12.5" font-weight="600">control</text>

      <!-- Comms feeding operator commands -->
      <rect x="556" y="14" width="124" height="40" rx="2" fill="#0b0d10" stroke="rgba(255,255,255,0.14)"/>
      <text x="618" y="38" text-anchor="middle" fill="#b2b8c2" font-family="${SANS}" font-size="12">Comms &amp; Foxglove</text>
      <line x1="618" y1="54" x2="618" y2="72" stroke="#4f7bd9" stroke-width="1.5" marker-end="url(#sub-blue)"/>

      <!-- Wheel odometry feedback back to Localisation -->
      <path d="M 618 124 L 618 190 L 252 190 L 252 185" fill="none" stroke="#8e95a2" stroke-width="1.2" stroke-dasharray="4 3" marker-end="url(#sub-arrow)"/>
      <text x="441" y="184" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="11">Wheel odometry feedback</text>
    </svg>
  </div>
  <figcaption class="figure-caption">
    Commands from autonomy and Comms converge at Teleop and control, while wheel encoder counts close the feedback loop back into Localisation.
  </figcaption>
</figure>`;
}

export function renderCostmapInflationDiagram() {
  const cols = 11;
  const rows = 5;
  const cell = 36;
  const x0 = 28;
  const y0 = 20;
  const cx = 5;
  const cy = 2;

  const cellsSvg = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const dist = Math.hypot(c - cx, r - cy);
      let fill = "#0b0d10";
      let label = "0";
      let textCol = "#666d7a";
      if (c === cx && r === cy) {
        fill = "#eceef2";
        label = "XX";
        textCol = "#0a0a0a";
      } else if (dist <= 1.45) {
        fill = "rgba(79,123,217,0.28)";
        label = "99";
        textCol = "#eceef2";
      } else if (dist <= 2.3) {
        fill = "rgba(79,123,217,0.14)";
        label = "40";
        textCol = "#b2b8c2";
      } else if (dist <= 3.2) {
        fill = "rgba(79,123,217,0.06)";
        label = "10";
        textCol = "#8e95a2";
      }
      const x = x0 + c * cell;
      const y = y0 + r * cell;
      cellsSvg.push(
        `<rect x="${x}" y="${y}" width="${cell}" height="${cell}" fill="${fill}" stroke="rgba(255,255,255,0.09)" stroke-width="1"/>` +
          `<text x="${x + cell / 2}" y="${y + cell / 2 + 4}" text-anchor="middle" fill="${textCol}" font-family="${SANS}" font-size="11" font-weight="${label === "XX" || label === "99" ? "600" : "400"}">${label}</text>`
      );
    }
  }

  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 220" role="img" aria-label="2D costmap grid showing a lethal boulder cell surrounded by an impassable 99-cost inscribed radius ring and decaying 40 and 10 buffer cells, with a safe curved route clearing the ring.">
      ${cellsSvg.join("\n      ")}
      <!-- Planned low-cost trajectory curving smoothly outside the 99 ring -->
      <path d="M 38 146 C 110 146, 138 28, 226 28 C 314 28, 342 128, 414 128" fill="none" stroke="#4f7bd9" stroke-width="2.2"/>
      <circle cx="38" cy="146" r="3.5" fill="#4f7bd9"/>

      <!-- Legend on right -->
      <g font-family="${SANS}" font-size="12">
        <rect x="454" y="34" width="14" height="14" rx="2" fill="#eceef2"/>
        <text x="478" y="45" fill="#eceef2" font-weight="500">Lethal obstacle (XX)</text>

        <rect x="454" y="64" width="14" height="14" rx="2" fill="rgba(79,123,217,0.28)" stroke="#4f7bd9"/>
        <text x="478" y="75" fill="#eceef2">Inscribed ring (99, no-go)</text>
        <text x="478" y="91" fill="#8e95a2" font-size="11">Half-width ≥ 0.34 m prevents wheel clip</text>

        <rect x="454" y="112" width="14" height="14" rx="2" fill="rgba(79,123,217,0.12)" stroke="rgba(255,255,255,0.18)"/>
        <text x="478" y="123" fill="#b2b8c2">Decaying buffer (40 → 10)</text>

        <line x1="454" y1="152" x2="470" y2="152" stroke="#4f7bd9" stroke-width="2.2"/>
        <text x="478" y="156" fill="#7098ec" font-weight="500">Lowest-cost planned route</text>
      </g>
    </svg>
  </div>
  <figcaption class="figure-caption">
    Inflating every obstacle cell outward by the rover's inscribed half-width turns six-wheel footprint clearance into a single-cell cost lookup.
  </figcaption>
</figure>`;
}

export function renderSerialPacketDiagram() {
  const fields = [
    { x: 20, w: 74, bytes: "0–1", val: "44 52", name: "Header", sub: 'ASCII "DR"', accent: false },
    { x: 98, w: 50, bytes: "2", val: "01", name: "Ver", sub: "v1", accent: false },
    { x: 152, w: 50, bytes: "3", val: "00", name: "Rsvd", sub: "Zero", accent: false },
    { x: 206, w: 124, bytes: "4–7", val: "01 00 00 00", name: "Sequence", sub: "uint32 LE", accent: false },
    { x: 334, w: 120, bytes: "8–11", val: "00 00 00 00", name: "Left target", sub: "int32 mrad/s", accent: false },
    { x: 458, w: 120, bytes: "12–15", val: "00 00 00 00", name: "Right target", sub: "int32 mrad/s", accent: false },
    { x: 582, w: 98, bytes: "16–17", val: "be 37", name: "CRC-16", sub: "CCITT-FALSE", accent: true },
  ];

  return `
<figure class="tech-figure">
  <div class="figure-frame">
    <svg viewBox="0 0 700 142" role="img" aria-label="18-byte little-endian DR v1 serial packet showing byte offsets 0 to 17 for header DR, version 1, reserved 0, 32-bit sequence counter, signed 32-bit left and right wheel targets in milliradians per second, and 16-bit CRC-16 checksum.">
      ${fields
        .map(
          (f) => `
        <text x="${f.x + f.w / 2}" y="22" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Byte ${f.bytes}</text>
        <rect x="${f.x}" y="30" width="${f.w}" height="44" rx="2" fill="${
            f.accent ? "rgba(79,123,217,0.14)" : "#0b0d10"
          }" stroke="${f.accent ? "#4f7bd9" : "rgba(255,255,255,0.16)"}" stroke-width="${f.accent ? "1.5" : "1"}"/>
        <text x="${f.x + f.w / 2}" y="57" text-anchor="middle" fill="${
            f.accent ? "#7098ec" : "#eceef2"
          }" font-family="'Geist Mono', 'SF Mono', Menlo, monospace" font-size="12" font-weight="${
            f.accent ? "600" : "400"
          }">${f.val}</text>
        <text x="${f.x + f.w / 2}" y="94" text-anchor="middle" fill="${
            f.accent ? "#7098ec" : "#eceef2"
          }" font-family="${SANS}" font-size="12" font-weight="500">${f.name}</text>
        <text x="${f.x + f.w / 2}" y="111" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="10.5">${f.sub}</text>`
        )
        .join("")}
      <!-- Span bracket showing CRC coverage over bytes 0..15 -->
      <path d="M 20 124 L 20 130 L 578 130 L 578 124" fill="none" stroke="rgba(79,123,217,0.5)" stroke-width="1"/>
      <line x1="578" y1="130" x2="631" y2="130" stroke="rgba(79,123,217,0.5)" stroke-width="1" stroke-dasharray="3 2"/>
    </svg>
  </div>
  <figcaption class="figure-caption">
    Startup arming frame (<code>seq = 1</code>, <code>left = 0</code>, <code>right = 0</code>): CRC-16 covers bytes 0 to 15, disarming <code>DriveCore</code> immediately if any bit flips on the wire.
  </figcaption>
</figure>`;
}

export function renderSkidSteerMathBlock() {
  return `
<div class="math-block" role="math" aria-label="left wheel speed equals v minus half track times omega; right wheel speed equals v plus half track times omega">
  <div class="math-row">
    <span>left wheel speed = <em>v</em> −</span>
    <span class="math-frac">
      <span class="math-num">track</span>
      <span class="math-den">2</span>
    </span>
    <span>× <em>ω</em></span>
  </div>
  <div class="math-row">
    <span>right wheel speed = <em>v</em> +</span>
    <span class="math-frac">
      <span class="math-num">track</span>
      <span class="math-den">2</span>
    </span>
    <span>× <em>ω</em></span>
  </div>
</div>`;
}

export function renderOusterMathBlock() {
  return `
<div class="math-block" role="math" aria-label="nearest level-ground hit equals LiDAR height divided by tangent of 21.2 degrees">
  <div class="math-row">
    <span>nearest level-ground hit =</span>
    <span class="math-frac">
      <span class="math-num">LiDAR height</span>
      <span class="math-den">tan(21.2°)</span>
    </span>
  </div>
</div>`;
}

export function renderInteractiveOusterFigure() {
  return `
<figure class="tech-figure" id="ouster-explorer">
  <div class="figure-frame">
    <svg id="ouster-svg" viewBox="0 0 700 226" role="img" aria-label="Interactive side-profile geometry of the Ouster OS1-128 vertical field of view, showing the 0.75 m stowed height limit, OAK-D Pro near-field view, and the nearest level-ground laser hit.">
      <!-- Ground line and distance ticks (0 m to 3.0 m, 175 px/m starting at rover centre x=96) -->
      <line x1="24" y1="186" x2="676" y2="186" stroke="rgba(255,255,255,0.22)" stroke-width="1.2"/>
      <g fill="#8e95a2" font-family="${SANS}" font-size="11.5" text-anchor="middle">
        <line x1="96" y1="186" x2="96" y2="192" stroke="rgba(255,255,255,0.22)"/>
        <text x="96" y="209">0 m</text>
        <line x1="271" y1="186" x2="271" y2="192" stroke="rgba(255,255,255,0.22)"/>
        <text x="271" y="209">1.0 m</text>
        <line x1="446" y1="186" x2="446" y2="192" stroke="rgba(255,255,255,0.22)"/>
        <text x="446" y="209">2.0 m</text>
        <line x1="621" y1="186" x2="621" y2="192" stroke="rgba(255,255,255,0.22)"/>
        <text x="621" y="209">3.0 m</text>
      </g>

      <!-- 0.75 m pre-run inspection height limit line (130 px/m vertical scale -> y = 186 - 0.75*130 = 88.5) -->
      <line x1="24" y1="88.5" x2="676" y2="88.5" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="5 4"/>
      <text x="670" y="81" text-anchor="end" fill="#8e95a2" font-family="${SANS}" font-size="11">0.75 m inspection height cap</text>

      <!-- Six-wheel rover side silhouette (1.06 m long -> 185 px? Use proportional 130 px/m scale on both axes? Wait: keep clean 130 px/m height & 175 px/m horizontal!) -->
      <!-- Chassis 0.18m to 0.71m height -> y=162.6 to y=93.7 -->
      <rect x="42" y="94" width="108" height="68" rx="2" fill="#13161b" stroke="#b2b8c2" stroke-width="1.3"/>
      <circle cx="56" cy="170" r="15.5" fill="#0b0d10" stroke="#8e95a2" stroke-width="1.3"/>
      <circle cx="96" cy="170" r="15.5" fill="#0b0d10" stroke="#8e95a2" stroke-width="1.3"/>
      <circle cx="136" cy="170" r="15.5" fill="#0b0d10" stroke="#8e95a2" stroke-width="1.3"/>

      <!-- Front OAK-D Pro near-field 15-deg downward cone -->
      <polygon points="150,98 370,186 168,186" fill="rgba(255,255,255,0.035)"/>
      <line x1="150" y1="98" x2="370" y2="186" stroke="#8e95a2" stroke-width="1" stroke-dasharray="3 3"/>
      <text x="236" y="176" fill="#8e95a2" font-family="${SANS}" font-size="11">OAK-D Pro covers near sand</text>

      <!-- Dynamic Ouster riser, sensor body, and +/-21.2 deg fan -->
      <line id="ouster-riser" x1="96" y1="94" x2="96" y2="64" stroke="#b2b8c2" stroke-width="2"/>
      <rect id="ouster-body" x="88" y="56" width="16" height="8" rx="1" fill="#eceef2"/>
      <polygon id="ouster-fan" points="96,60 676,12 676,186 520,186" fill="rgba(79,123,217,0.13)"/>
      <line id="ouster-top-ray" x1="96" y1="60" x2="676" y2="12" stroke="#4f7bd9" stroke-width="1.2" stroke-dasharray="4 3"/>
      <line id="ouster-bot-ray" x1="96" y1="60" x2="520" y2="186" stroke="#4f7bd9" stroke-width="1.9"/>
      <circle id="ouster-hit-dot" cx="520" cy="186" r="3.8" fill="#4f7bd9"/>
      <text id="ouster-hit-label" x="520" y="174" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="12" font-weight="500">2.42 m first hit</text>
    </svg>

    <div class="kalman-metrics" role="status" aria-live="polite">
      <div class="metric-cell">
        <span class="metric-name">LiDAR base height</span>
        <span class="metric-val" id="ouster-out-base">0.94 m</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Top of sensor</span>
        <span class="metric-val" id="ouster-out-top">1.00 m</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Nearest ground hit</span>
        <span class="metric-val is-accent" id="ouster-out-hit">2.42 m</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">75 cm stowed box</span>
        <span class="metric-val" id="ouster-out-box">Fold for inspection</span>
      </div>
    </div>

    <div class="kalman-controls" style="grid-template-columns: 1fr;">
      <div class="slider-field">
        <div class="slider-label-row">
          <label for="slider-ouster-h">LiDAR mount height above sand</label>
          <span class="slider-readout" id="label-ouster-h">0.94 m</span>
        </div>
        <input id="slider-ouster-h" class="accent-slider" type="range" min="0.50" max="0.96" step="0.01" value="0.94"/>
      </div>
    </div>

    <div class="preset-bar" id="ouster-preset-bar" role="group" aria-label="LiDAR mount presets">
      <div class="preset-indicator" id="ouster-preset-indicator" aria-hidden="true"></div>
      <button type="button" class="preset-btn ouster-preset" data-h="0.60" aria-pressed="false">Low mount (0.60 m)</button>
      <button type="button" class="preset-btn ouster-preset" data-h="0.69" aria-pressed="false">Under 75 cm cap (0.69 m)</button>
      <button type="button" class="preset-btn ouster-preset" data-h="0.94" aria-pressed="true">Central 23 cm riser (0.94 m)</button>
    </div>
  </div>
  <figcaption class="figure-caption">
    Raising the Ouster clears the rover chassis across 360 degrees at the cost of pushing the innermost scan ring farther out and exceeding the 0.75 m starting box unless stowed.
  </figcaption>
</figure>`;
}

