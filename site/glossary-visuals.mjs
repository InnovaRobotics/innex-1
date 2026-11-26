const SANS = "'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif";

export const GLOSSARY_VISUALS = {
  apriltag: {
    type: "img",
    src: "images/apriltag.png",
    alt: "AprilTag 36h11 visual fiducial marker",
    fit: "contain",
    pad: true,
  },

  "bldc-motor": {
    type: "img",
    src: "images/bldc.jpg",
    alt: "Brushless DC motor stator windings",
    fit: "cover",
  },

  "e-stop": {
    type: "img",
    src: "images/estop.jpg",
    alt: "Latching red mushroom emergency stop button",
    fit: "cover",
  },

  "point-cloud": {
    type: "img",
    src: "images/point-cloud.jpg",
    alt: "3D LiDAR point cloud captured by an Ouster OS1",
    fit: "cover",
  },

  costmap: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <!-- 9x4 grid around lethal cell -->
    <g transform="translate(32, 14)" stroke="rgba(255,255,255,0.08)" stroke-width="1">
      <rect x="72" y="20" width="96" height="60" fill="rgba(79,123,217,0.1)" stroke="none"/>
      <rect x="96" y="30" width="48" height="40" fill="rgba(79,123,217,0.22)" stroke="none"/>
      <rect x="108" y="36" width="24" height="28" fill="#eceef2" stroke="none"/>
      <line x1="0" y1="0" x2="216" y2="0"/><line x1="0" y1="20" x2="216" y2="20"/>
      <line x1="0" y1="40" x2="216" y2="40"/><line x1="0" y1="60" x2="216" y2="60"/>
      <line x1="0" y1="80" x2="216" y2="80"/>
      <line x1="0" y1="0" x2="0" y2="80"/><line x1="36" y1="0" x2="36" y2="80"/>
      <line x1="72" y1="0" x2="72" y2="80"/><line x1="108" y1="0" x2="108" y2="80"/>
      <line x1="144" y1="0" x2="144" y2="80"/><line x1="180" y1="0" x2="180" y2="80"/>
      <line x1="216" y1="0" x2="216" y2="80"/>
      <path d="M 10 68 C 54 68, 72 10, 120 10 C 168 10, 184 54, 208 54" fill="none" stroke="#4f7bd9" stroke-width="1.8"/>
    </g>
    <text x="262" y="46" fill="#eceef2" font-family="${SANS}" font-size="11">Obstacle</text>
    <text x="262" y="64" fill="#7098ec" font-family="${SANS}" font-size="11">Inflated cost</text>
  </svg>`,

  covariance: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <line x1="36" y1="84" x2="220" y2="84" stroke="rgba(255,255,255,0.16)" stroke-width="1"/>
    <line x1="36" y1="84" x2="36" y2="20" stroke="rgba(255,255,255,0.16)" stroke-width="1"/>
    <g transform="translate(128, 52) rotate(-22)">
      <ellipse cx="0" cy="0" rx="58" ry="26" fill="rgba(79,123,217,0.08)" stroke="#8e95a2" stroke-width="1" stroke-dasharray="4 3"/>
      <ellipse cx="0" cy="0" rx="32" ry="14" fill="rgba(79,123,217,0.2)" stroke="#4f7bd9" stroke-width="1.5"/>
      <circle cx="0" cy="0" r="3" fill="#eceef2"/>
    </g>
    <text x="234" y="46" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">1σ confidence</text>
    <text x="234" y="64" fill="#8e95a2" font-family="${SANS}" font-size="11">2σ outer bound</text>
  </svg>`,

  ekf: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <line x1="24" y1="88" x2="316" y2="88" stroke="rgba(255,255,255,0.18)" stroke-width="1"/>
    <path d="M 36 88 Q 108 86 154 56 Q 192 32 230 56 Q 274 86 308 88" fill="none" stroke="#8e95a2" stroke-width="1.3"/>
    <path d="M 52 88 Q 92 86 112 36 Q 124 14 136 36 Q 156 86 196 88" fill="none" stroke="#eceef2" stroke-width="1.3" stroke-dasharray="3 3"/>
    <path d="M 66 88 Q 104 86 122 28 Q 132 8 142 28 Q 160 86 198 88 Z" fill="rgba(79,123,217,0.16)" stroke="none"/>
    <path d="M 66 88 Q 104 86 122 28 Q 132 8 142 28 Q 160 86 198 88" fill="none" stroke="#4f7bd9" stroke-width="1.9"/>
    <text x="228" y="34" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">Fused posterior</text>
    <text x="228" y="50" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Weighted by variance</text>
  </svg>`,

  encoder: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <text x="22" y="37" fill="#b2b8c2" font-family="${SANS}" font-size="11">Ch A</text>
    <path d="M 60 42 L 84 42 L 84 20 L 124 20 L 124 42 L 164 42 L 164 20 L 204 20 L 204 42 L 244 42 L 244 20 L 284 20 L 284 42 L 310 42" fill="none" stroke="#eceef2" stroke-width="1.5"/>
    <text x="22" y="79" fill="#7098ec" font-family="${SANS}" font-size="11" font-weight="500">Ch B</text>
    <path d="M 60 84 L 104 84 L 104 62 L 144 62 L 144 84 L 184 84 L 184 62 L 224 62 L 224 84 L 264 84 L 264 62 L 304 62 L 304 84 L 310 84" fill="none" stroke="#4f7bd9" stroke-width="1.6"/>
    <!-- 90 deg phase guide -->
    <line x1="84" y1="16" x2="84" y2="92" stroke="rgba(255,255,255,0.2)" stroke-width="1" stroke-dasharray="2 2"/>
    <line x1="104" y1="16" x2="104" y2="92" stroke="rgba(79,123,217,0.45)" stroke-width="1" stroke-dasharray="2 2"/>
    <text x="94" y="13" text-anchor="middle" fill="#8e95a2" font-family="${SANS}" font-size="10">90° offset</text>
  </svg>`,

  frame: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <!-- Rover outline -->
    <rect x="82" y="42" width="76" height="40" rx="2" fill="none" stroke="rgba(255,255,255,0.22)" stroke-width="1.2" stroke-dasharray="4 3"/>
    <!-- REP 103 axes at base_link -->
    <line x1="120" y1="62" x2="120" y2="18" stroke="#b2b8c2" stroke-width="1.5"/>
    <path d="M 116.5 23 L 120 17 L 123.5 23" fill="none" stroke="#b2b8c2" stroke-width="1.5"/>
    <text x="128" y="24" fill="#b2b8c2" font-family="${SANS}" font-size="11">+z up</text>

    <line x1="120" y1="62" x2="74" y2="86" stroke="#eceef2" stroke-width="1.5"/>
    <path d="M 77 80.5 L 73 86.5 L 80.5 87" fill="none" stroke="#eceef2" stroke-width="1.5"/>
    <text x="34" y="94" fill="#eceef2" font-family="${SANS}" font-size="11">+y left</text>

    <line x1="120" y1="62" x2="206" y2="62" stroke="#4f7bd9" stroke-width="1.9"/>
    <path d="M 200 58.5 L 207 62 L 200 65.5" fill="none" stroke="#4f7bd9" stroke-width="1.8"/>
    <text x="216" y="66" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">+x forward (REP 103)</text>
    <circle cx="120" cy="62" r="3" fill="#4f7bd9"/>
  </svg>`,

  icp: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <g transform="translate(-14, 8) rotate(-6 140 54)">
      <path d="M 64 88 L 64 26 L 214 26" fill="none" stroke="#8e95a2" stroke-width="1.4" stroke-dasharray="5 4"/>
    </g>
    <path d="M 64 88 L 64 26 L 214 26" fill="none" stroke="#eceef2" stroke-width="1.8"/>
    <circle cx="64" cy="70" r="2.2" fill="#4f7bd9"/><circle cx="64" cy="46" r="2.2" fill="#4f7bd9"/>
    <circle cx="96" cy="26" r="2.2" fill="#4f7bd9"/><circle cx="138" cy="26" r="2.2" fill="#4f7bd9"/><circle cx="180" cy="26" r="2.2" fill="#4f7bd9"/>
    <path d="M 122 72 L 156 58" fill="none" stroke="#4f7bd9" stroke-width="1.7"/>
    <path d="M 150 56.5 L 157 57.5 L 153 63" fill="none" stroke="#4f7bd9" stroke-width="1.6"/>
    <text x="232" y="48" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">Scan shift</text>
    <text x="232" y="65" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Rigid wall match</text>
  </svg>`,

  "lidar-odometry": `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <g transform="translate(-14, 8) rotate(-6 140 54)">
      <path d="M 64 88 L 64 26 L 214 26" fill="none" stroke="#8e95a2" stroke-width="1.4" stroke-dasharray="5 4"/>
    </g>
    <path d="M 64 88 L 64 26 L 214 26" fill="none" stroke="#eceef2" stroke-width="1.8"/>
    <circle cx="64" cy="70" r="2.2" fill="#4f7bd9"/><circle cx="64" cy="46" r="2.2" fill="#4f7bd9"/>
    <circle cx="96" cy="26" r="2.2" fill="#4f7bd9"/><circle cx="138" cy="26" r="2.2" fill="#4f7bd9"/><circle cx="180" cy="26" r="2.2" fill="#4f7bd9"/>
    <path d="M 122 72 L 156 58" fill="none" stroke="#4f7bd9" stroke-width="1.7"/>
    <path d="M 150 56.5 L 157 57.5 L 153 63" fill="none" stroke="#4f7bd9" stroke-width="1.6"/>
    <text x="232" y="48" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">Scan shift</text>
    <text x="232" y="65" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Rigid wall match</text>
  </svg>`,

  imu: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <!-- Sensor block -->
    <polygon points="140,46 174,34 202,48 168,60" fill="#151820" stroke="#eceef2" stroke-width="1.3"/>
    <polygon points="140,46 168,60 168,74 140,60" fill="#101217" stroke="#b2b8c2" stroke-width="1.2"/>
    <polygon points="168,60 202,48 202,62 168,74" fill="#12151c" stroke="#b2b8c2" stroke-width="1.2"/>
    <!-- Vertical yaw axis + blue rotation arc -->
    <line x1="171" y1="14" x2="171" y2="47" stroke="#4f7bd9" stroke-width="1.5"/>
    <path d="M 154 24 A 20 8 0 1 1 187 26" fill="none" stroke="#4f7bd9" stroke-width="1.7"/>
    <path d="M 183 22 L 188 26.5 L 182 28.5" fill="none" stroke="#4f7bd9" stroke-width="1.5"/>
    <text x="200" y="27" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">Yaw rate (gyro)</text>
    <!-- Roll / pitch axes -->
    <line x1="192" y1="62" x2="234" y2="78" stroke="#8e95a2" stroke-width="1.3"/>
    <line x1="148" y1="64" x2="104" y2="80" stroke="#8e95a2" stroke-width="1.3"/>
    <text x="58" y="86" fill="#8e95a2" font-family="${SANS}" font-size="11">Pitch</text>
    <text x="242" y="84" fill="#8e95a2" font-family="${SANS}" font-size="11">Roll</text>
  </svg>`,

  lidar: {
    type: "img",
    src: "images/ouster-os1.png",
    alt: "Ouster OS1-128 LiDAR sensor",
    fit: "cover",
  },

  pose: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <line x1="44" y1="86" x2="216" y2="86" stroke="rgba(255,255,255,0.22)" stroke-width="1.2"/>
    <line x1="44" y1="86" x2="44" y2="18" stroke="rgba(255,255,255,0.22)" stroke-width="1.2"/>
    <line x1="142" y1="86" x2="142" y2="48" stroke="#8e95a2" stroke-width="1" stroke-dasharray="3 3"/>
    <line x1="44" y1="48" x2="142" y2="48" stroke="#8e95a2" stroke-width="1" stroke-dasharray="3 3"/>
    <line x1="142" y1="48" x2="188" y2="48" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
    <line x1="142" y1="48" x2="182" y2="24" stroke="#4f7bd9" stroke-width="1.9"/>
    <path d="M 168 48 A 26 26 0 0 0 164 35" fill="none" stroke="#4f7bd9" stroke-width="1.4"/>
    <circle cx="142" cy="48" r="3.5" fill="#eceef2"/>
    <text x="224" y="44" fill="#eceef2" font-family="${SANS}" font-size="11.5">(x, y) position</text>
    <text x="224" y="62" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">θ heading</text>
  </svg>`,

  "skid-steer": `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <g transform="translate(116, 54)">
      <rect x="-26" y="-18" width="52" height="36" rx="2" fill="#14171c" stroke="#eceef2" stroke-width="1.4"/>
      <!-- Left wheels (slower) -->
      <rect x="-24" y="-24" width="12" height="4" rx="1" fill="#8e95a2"/>
      <rect x="-6" y="-24" width="12" height="4" rx="1" fill="#8e95a2"/>
      <rect x="12" y="-24" width="12" height="4" rx="1" fill="#8e95a2"/>
      <line x1="-22" y1="-32" x2="4" y2="-32" stroke="#8e95a2" stroke-width="1.4"/>
      <!-- Right wheels (faster in blue) -->
      <rect x="-24" y="20" width="12" height="4" rx="1" fill="#4f7bd9"/>
      <rect x="-6" y="20" width="12" height="4" rx="1" fill="#4f7bd9"/>
      <rect x="12" y="20" width="12" height="4" rx="1" fill="#4f7bd9"/>
      <line x1="-22" y1="32" x2="32" y2="32" stroke="#4f7bd9" stroke-width="1.8"/>
      <path d="M 27 28.5 L 33 32 L 27 35.5" fill="none" stroke="#4f7bd9" stroke-width="1.6"/>
      <!-- Resulting left turn curve -->
      <path d="M 28 0 Q 52 -2 62 -24" fill="none" stroke="#4f7bd9" stroke-width="1.6" stroke-dasharray="3 3"/>
    </g>
    <text x="212" y="46" fill="#7098ec" font-family="${SANS}" font-size="11.5" font-weight="500">Right side faster</text>
    <text x="212" y="64" fill="#8e95a2" font-family="${SANS}" font-size="11">Turns rover left</text>
  </svg>`,

  watchdog: `<svg viewBox="0 0 340 108" aria-hidden="true">
    <rect width="340" height="108" fill="#0b0d10"/>
    <!-- Command ticks -->
    <text x="20" y="34" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Input</text>
    <g stroke="#eceef2" stroke-width="1.6">
      <line x1="66" y1="38" x2="66" y2="20"/>
      <line x1="94" y1="38" x2="94" y2="20"/>
      <line x1="122" y1="38" x2="122" y2="20"/>
      <line x1="150" y1="38" x2="150" y2="20"/>
    </g>
    <line x1="60" y1="38" x2="314" y2="38" stroke="rgba(255,255,255,0.16)" stroke-width="1"/>
    <!-- Timeout span -->
    <line x1="150" y1="16" x2="150" y2="92" stroke="rgba(255,255,255,0.22)" stroke-width="1" stroke-dasharray="2 3"/>
    <line x1="236" y1="16" x2="236" y2="92" stroke="#4f7bd9" stroke-width="1.3" stroke-dasharray="3 3"/>
    <text x="193" y="29" text-anchor="middle" fill="#7098ec" font-family="${SANS}" font-size="10.5">250 ms silence</text>
    <!-- Motor output drops to 0 -->
    <text x="20" y="76" fill="#8e95a2" font-family="${SANS}" font-size="10.5">Motors</text>
    <path d="M 60 62 L 236 62 L 236 84 L 314 84" fill="none" stroke="#4f7bd9" stroke-width="1.9"/>
    <text x="276" y="77" text-anchor="middle" fill="#eceef2" font-family="${SANS}" font-size="10.5">Disarmed (0)</text>
  </svg>`,
};
