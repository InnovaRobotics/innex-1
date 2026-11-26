export function renderIcpWallDiagram() {
  return `
<figure class="tech-figure" aria-labelledby="fig-icp-title">
  <figcaption id="fig-icp-title" class="figure-caption-top">
    Matching consecutive top-down LiDAR wall scans measures rover motion on sand while the beacon anchors which end of the pit is which.
  </figcaption>
  <div class="figure-frame">
    <svg viewBox="0 0 720 364" role="img" aria-label="Top-down diagram of the 7.9 m by 4.4 m Moon Yard showing a previous LiDAR wall scan in dashed grey aligned onto the current wall scan in white, plus the 6.6 m 71-degree sightline to the start-corner beacon.">
      <defs>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 1 1.5 L 8.5 5 L 1 8.5" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="arrow-muted" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 1 1.5 L 8.5 5 L 1 8.5" fill="none" stroke="#a2a7b0" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>

      <!-- Beacon callout above top wall so no lines cross text -->
      <text x="134" y="26" text-anchor="middle" fill="#ededed" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">Single-face beacon</text>
      <line x1="134" y1="31" x2="134" y2="48" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>

      <!-- Arena interior (7.9 m x 4.4 m -> 552 x 244 px) -->
      <rect x="84" y="52" width="552" height="244" fill="#0c0d10" stroke="#ededed" stroke-width="1.25"/>

      <!-- Zone dividers (subtle dashed reference lines) -->
      <line x1="224" y1="52" x2="224" y2="190" stroke="rgba(255,255,255,0.13)" stroke-width="1" stroke-dasharray="4 4"/>
      <line x1="84" y1="190" x2="224" y2="190" stroke="rgba(255,255,255,0.13)" stroke-width="1" stroke-dasharray="4 4"/>
      <line x1="444" y1="52" x2="444" y2="296" stroke="rgba(255,255,255,0.13)" stroke-width="1" stroke-dasharray="4 4"/>

      <!-- Zone labels placed clear of rays -->
      <text x="96" y="108" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">Start zone</text>
      <text x="96" y="280" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">Construction &amp; berm</text>
      <text x="296" y="82" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">Obstacle zone</text>
      <text x="462" y="82" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">Excavation zone</text>

      <!-- Shifted unaligned scan at t - 100 ms (dashed grey) -->
      <g transform="translate(-18, 10) rotate(-3.5 360 174)">
        <rect x="84" y="52" width="552" height="244" fill="none" stroke="#868b94" stroke-width="1.1" stroke-dasharray="6 5" opacity="0.65"/>
      </g>

      <!-- LiDAR return dots along current rigid walls -->
      <g fill="#ededed">
        <circle cx="130" cy="52" r="2"/><circle cx="185" cy="52" r="2"/><circle cx="245" cy="52" r="2"/><circle cx="310" cy="52" r="2"/><circle cx="375" cy="52" r="2"/><circle cx="440" cy="52" r="2"/><circle cx="510" cy="52" r="2"/><circle cx="580" cy="52" r="2"/>
        <circle cx="145" cy="296" r="2"/><circle cx="215" cy="296" r="2"/><circle cx="290" cy="296" r="2"/><circle cx="360" cy="296" r="2"/><circle cx="435" cy="296" r="2"/><circle cx="505" cy="296" r="2"/><circle cx="575" cy="296" r="2"/>
        <circle cx="636" cy="90" r="2"/><circle cx="636" cy="140" r="2"/><circle cx="636" cy="190" r="2"/><circle cx="636" cy="245" r="2"/>
      </g>

      <!-- Beacon bar on top wall facing south towards construction zone -->
      <line x1="114" y1="52" x2="154" y2="52" stroke="#ededed" stroke-width="3.5"/>
      <line x1="134" y1="52" x2="134" y2="75" stroke="#a2a7b0" stroke-width="1.2" marker-end="url(#arrow-muted)"/>

      <!-- Oblique sightline from excavation zone (6.6 m at ~71 deg off normal) -->
      <line x1="544" y1="186" x2="138" y2="55" stroke="#868b94" stroke-width="1" stroke-dasharray="3 4"/>
      <path d="M 134 69 A 17 17 0 0 0 150 59" fill="none" stroke="#a2a7b0" stroke-width="1"/>
      <rect x="266" y="101" width="166" height="18" fill="#0c0d10"/>
      <text x="349" y="114" text-anchor="middle" fill="#a2a7b0" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="11">6.6 m · 71° off face</text>

      <!-- Previous rover pose (ghosted) -->
      <g transform="translate(318, 200) rotate(-8)">
        <rect x="-18" y="-12" width="36" height="24" rx="1.5" fill="none" stroke="#868b94" stroke-width="1" stroke-dasharray="3 3"/>
      </g>

      <!-- Radial laser rays from rover to rigid walls -->
      <g stroke="#4f7bd9" stroke-width="0.9" opacity="0.42">
        <line x1="374" y1="184" x2="310" y2="52"/>
        <line x1="374" y1="184" x2="440" y2="52"/>
        <line x1="374" y1="184" x2="636" y2="140"/>
        <line x1="374" y1="184" x2="435" y2="296"/>
      </g>

      <!-- Current rover pose in blue accent + ICP alignment shift -->
      <line x1="318" y1="200" x2="364" y2="187" stroke="#4f7bd9" stroke-width="1.8" marker-end="url(#arrow-blue)"/>
      <g transform="translate(374, 184) rotate(-4)">
        <rect x="-19" y="-12.5" width="38" height="25" rx="1.5" fill="rgba(79,123,217,0.18)" stroke="#4f7bd9" stroke-width="1.5"/>
        <line x1="0" y1="0" x2="15" y2="0" stroke="#4f7bd9" stroke-width="1.5"/>
      </g>

      <!-- Callout annotations with clean background clearance -->
      <rect x="292" y="218" width="140" height="18" fill="#0c0d10"/>
      <text x="362" y="231" text-anchor="middle" fill="#6e96ea" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="11.5">ICP shift (Δx, Δy, Δθ)</text>

      <!-- Footer legend placed cleanly below rotated scan -->
      <text x="84" y="344" fill="#868b94" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="11">7.9 m × 4.4 m pit (live scan only)</text>
      <text x="636" y="344" text-anchor="end" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">Dashed: scan at t − 100 ms · Solid: scan at t</text>
    </svg>
  </div>
  <p class="figure-cue">
    Compare the dashed grey pit contour from 100 ms earlier against the solid white wall dots: sliding one scan onto the other recovers the blue motion vector even when all six tyres spin in loose sand.
  </p>
</figure>`;
}

export function renderRep105Diagram() {
  return `
<figure class="tech-figure" aria-labelledby="fig-rep105-title">
  <figcaption id="fig-rep105-title" class="figure-caption-top">
    REP 105 isolates discrete beacon corrections inside <code>map → odom</code> so <code>odom → base_link</code> stays continuous mid-turn.
  </figcaption>
  <div class="figure-frame">
    <svg viewBox="0 0 720 332" role="img" aria-label="Diagram showing the map to odom to base_link frame chain above a top-down boulder-avoidance manoeuvre where a 25 cm drift correction shifts map to odom without jerking base_link.">
      <defs>
        <marker id="rep-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1 1.5 L 8.5 5 L 1 8.5" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
        <marker id="rep-white" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M 1 1.5 L 8.5 5 L 1 8.5" fill="none" stroke="#ededed" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </marker>
      </defs>

      <!-- Top half: TF single-parent chain (boxes 142px wide, 125px arrow spans) -->
      <rect x="24" y="20" width="142" height="58" rx="2" fill="#0c0d10" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
      <text x="38" y="44" fill="#ededed" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="13" font-weight="600">map</text>
      <text x="38" y="63" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11">Arena-fixed origin</text>

      <line x1="166" y1="49" x2="285" y2="49" stroke="#4f7bd9" stroke-width="1.75" marker-end="url(#rep-blue)"/>
      <text x="226" y="37" text-anchor="middle" fill="#6e96ea" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11" font-weight="500">Beacon fix</text>
      <text x="226" y="67" text-anchor="middle" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="10.5">absorbs 25 cm jump</text>

      <rect x="289" y="20" width="142" height="58" rx="2" fill="#0c0d10" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
      <text x="303" y="44" fill="#ededed" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="13" font-weight="600">odom</text>
      <text x="303" y="63" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11">Smooth local origin</text>

      <line x1="431" y1="49" x2="550" y2="49" stroke="#ededed" stroke-width="1.5" marker-end="url(#rep-white)"/>
      <text x="491" y="37" text-anchor="middle" fill="#ededed" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11">Wheels + IMU + ICP</text>
      <text x="491" y="67" text-anchor="middle" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="10.5">never jumps</text>

      <rect x="554" y="20" width="142" height="58" rx="2" fill="#0c0d10" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
      <text x="568" y="44" fill="#ededed" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="13" font-weight="600">base_link</text>
      <text x="568" y="63" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11">Under middle axle</text>

      <!-- Divider -->
      <line x1="24" y1="102" x2="696" y2="102" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>

      <!-- Bottom half: Physical trajectory around a boulder -->
      <path d="M 56 254 C 172 254, 244 162, 372 156 C 458 152, 548 166, 672 166" fill="none" stroke="#868b94" stroke-width="1.3" stroke-dasharray="5 5"/>
      <text x="684" y="148" text-anchor="end" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">Drifted odom path (smooth, 25 cm sideways error)</text>

      <path d="M 56 254 C 172 264, 244 204, 372 200 C 458 197, 548 210, 672 210" fill="none" stroke="#ededed" stroke-width="1.6"/>
      <text x="684" y="232" text-anchor="end" fill="#ededed" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">True arena path after map → odom shift</text>

      <!-- Boulder hazard -->
      <circle cx="372" cy="256" r="22" fill="#16181d" stroke="#a2a7b0" stroke-width="1.25"/>
      <text x="372" y="294" text-anchor="middle" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11">35 cm boulder</text>

      <!-- Ghost drifted rover vs snapped map->odom offset -->
      <rect x="353" y="145" width="38" height="22" rx="1.5" fill="none" stroke="#868b94" stroke-width="1" stroke-dasharray="3 3"/>
      <line x1="372" y1="170" x2="372" y2="186" stroke="#4f7bd9" stroke-width="1.8" marker-end="url(#rep-blue)"/>
      <text x="386" y="182" fill="#6e96ea" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="11">map → odom shifts 25 cm</text>

      <!-- Rover on true curve -->
      <rect x="353" y="189" width="38" height="22" rx="1.5" fill="rgba(79,123,217,0.18)" stroke="#4f7bd9" stroke-width="1.5"/>
      <circle cx="56" cy="254" r="3.5" fill="#ededed"/>
      <text x="56" y="276" fill="#868b94" font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11">Start</text>
    </svg>
  </div>
  <p class="figure-cue">
    Follow the blue arrow mid-turn past the boulder: shifting the <code>map → odom</code> origin corrects the 25 cm drift for the route planner while the local controller keeps tracking the smooth curve without a wheel jerk.
  </p>
</figure>`;
}

export function renderKalmanMathBlock1() {
  return `
<div class="math-block" role="math" aria-label="weight equals prediction variance divided by prediction variance plus measurement variance">
  <div class="math-row">
    <span>weight (<em>K</em>) =</span>
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
<figure class="tech-figure" id="kalman-explorer" aria-labelledby="fig-kalman-title">
  <figcaption id="fig-kalman-title" class="figure-caption-top">
    Weighting two noisy sensors by their variances produces a fused pose (<span style="color:#6e96ea">blue</span>) more certain than either sensor alone.
  </figcaption>
  <div class="figure-frame">
    <svg id="kalman-svg" viewBox="0 0 720 236" role="img" aria-label="Probability density curves for wheel prediction at 2.00 m, beacon sighting at 1.60 m, and the Kalman-fused estimate.">
      <!-- Baseline and evenly spaced x-axis ticks (1.20 m, 1.60 m, 2.00 m, 2.40 m, 2.70 m) -->
      <line x1="44" y1="194" x2="684" y2="194" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
      <g fill="#868b94" font-family="Geist Mono, SF Mono, Menlo, monospace" font-size="11" text-anchor="middle">
        <line x1="88.7" y1="194" x2="88.7" y2="200" stroke="rgba(255,255,255,0.2)"/>
        <text x="88.7" y="216">1.20 m</text>
        <line x1="237.5" y1="194" x2="237.5" y2="200" stroke="rgba(255,255,255,0.35)"/>
        <text x="237.5" y="216" fill="#ededed">1.60 m</text>
        <line x1="386.3" y1="194" x2="386.3" y2="200" stroke="rgba(255,255,255,0.35)"/>
        <text x="386.3" y="216" fill="#a2a7b0">2.00 m</text>
        <line x1="535.2" y1="194" x2="535.2" y2="200" stroke="rgba(255,255,255,0.2)"/>
        <text x="535.2" y="216">2.40 m</text>
        <line x1="646.8" y1="194" x2="646.8" y2="200" stroke="rgba(255,255,255,0.2)"/>
        <text x="646.8" y="216">2.70 m</text>
      </g>

      <!-- Legend inside plot top-right -->
      <g font-family="-apple-system, BlinkMacSystemFont, Inter, sans-serif" font-size="11.5">
        <line x1="468" y1="26" x2="492" y2="26" stroke="#868b94" stroke-width="1.5"/>
        <text x="500" y="30" fill="#a2a7b0">Wheel prediction (2.00 m)</text>
        <line x1="468" y1="46" x2="492" y2="46" stroke="#ededed" stroke-width="1.4" stroke-dasharray="4 3"/>
        <text x="500" y="50" fill="#ededed">Beacon sighting (1.60 m)</text>
        <line x1="468" y1="66" x2="492" y2="66" stroke="#4f7bd9" stroke-width="2"/>
        <text x="500" y="70" fill="#6e96ea" font-weight="500">Fused EKF estimate</text>
      </g>

      <!-- Dynamic curves -->
      <path id="curve-pred" fill="none" stroke="#868b94" stroke-width="1.5" d=""/>
      <path id="curve-meas" fill="none" stroke="#ededed" stroke-width="1.4" stroke-dasharray="4 3" d=""/>
      <path id="curve-fused-fill" fill="rgba(79,123,217,0.14)" stroke="none" d=""/>
      <path id="curve-fused" fill="none" stroke="#4f7bd9" stroke-width="2.1" d=""/>
      <line id="line-fused-mean" x1="252.4" y1="30" x2="252.4" y2="194" stroke="#4f7bd9" stroke-width="1" stroke-dasharray="2 3"/>
    </svg>

    <div class="kalman-metrics" role="status" aria-live="polite">
      <div class="metric-cell">
        <span class="metric-name">Prediction var (<em>P</em>)</span>
        <span class="metric-val" id="out-p">0.090 m²</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Beacon var (<em>R</em>)</span>
        <span class="metric-val" id="out-r">0.010 m²</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Kalman gain (<em>K</em>)</span>
        <span class="metric-val is-accent" id="out-k">0.900</span>
      </div>
      <div class="metric-cell">
        <span class="metric-name">Updated pose · σ²</span>
        <span class="metric-val is-accent" id="out-x">1.64 m · 0.009 m²</span>
      </div>
    </div>

    <div class="kalman-controls">
      <div class="slider-field">
        <div class="slider-label-row">
          <label for="slider-pred">Wheel odometry typical error (σ<sub>pred</sub>)</label>
          <span class="slider-readout" id="label-pred">0.30 m</span>
        </div>
        <input id="slider-pred" type="range" min="0.05" max="0.60" step="0.01" value="0.30"/>
      </div>
      <div class="slider-field">
        <div class="slider-label-row">
          <label for="slider-meas">Beacon sighting typical error (σ<sub>meas</sub>)</label>
          <span class="slider-readout" id="label-meas">0.10 m</span>
        </div>
        <input id="slider-meas" class="accent-slider" type="range" min="0.02" max="3.00" step="0.01" value="0.10"/>
      </div>
    </div>

    <div class="preset-bar" role="group" aria-label="Kalman filter presets">
      <button type="button" class="preset-btn" data-pred="0.30" data-meas="0.10" aria-pressed="true">Worked example (0.30 m vs 0.10 m)</button>
      <button type="button" class="preset-btn" data-pred="0.30" data-meas="0.02" aria-pressed="false">Sharp beacon (σ → 0, K → 1)</button>
      <button type="button" class="preset-btn" data-pred="0.30" data-meas="3.00" aria-pressed="false">Blurry far tag (R = 9.0 m², K &lt; 0.01)</button>
    </div>
  </div>
  <p class="figure-cue">
    Drag either error slider or try the two extreme presets to check the formula: as beacon uncertainty shrinks, <em>K</em> approaches 1 and snaps to 1.60 m; when beacon variance climbs to 9.0 m², <em>K</em> drops below 0.01 and trusts wheel odometry.
  </p>
</figure>`;
}
