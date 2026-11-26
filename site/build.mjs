import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  renderIcpWallDiagram,
  renderRep105Diagram,
  renderKalmanMathBlock1,
  renderKalmanMathBlock2,
  renderInteractiveKalmanFigure,
} from "./diagrams.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");
const SOURCE_MD = path.join(REPO_ROOT, "docs/system/localisation.md");
const DIST_DIR = path.join(__dirname, "dist");

function slugify(text) {
  return text
    .replace(/`([^`]+)`/g, "$1")
    .trim()
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-");
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function smartTypography(text) {
  return text
    .replace(/\.\.\./g, "…")
    .replace(/(\w)'(\w)/g, "$1’$2")
    .replace(/(^|[\s(])"([^"]+)"/g, "$1“$2”");
}

function formatInline(raw) {
  const codeSpans = [];
  const plainMeasurementRe =
    /^-?\d+(?:\.\d+)?\s*(?:m|cm|mm)?(?:\s*(?:x|×|\/|\*|=|-)\s*-?\d+(?:\.\d+)?\s*(?:m|cm|mm)?)?\s*(?:m|cm|mm|ms|s|W|Wh|kg|Hz|kbps|degrees?|per cent|m\^2)?$/i;

  let text = raw.replace(/`([^`]+)`/g, (_, code) => {
    // Keep physical numbers and units in flowing body text instead of wrapping every measurement in a box
    if (plainMeasurementRe.test(code.trim())) {
      const cleanQty = escapeHtml(code)
        .replace(/\s+x\s+/g, "\u00a0×\u00a0")
        .replace(/m\^2/g, "m²")
        .replace(/\s+(m|cm|mm|ms|s|W|Wh|kg|Hz|kbps|m²)\b/g, "\u00a0$1");
      const idx = codeSpans.length;
      codeSpans.push(cleanQty);
      return `\u0000CODE${idx}\u0000`;
    }
    const idx = codeSpans.length;
    const formattedCode = escapeHtml(code).replace(/ -&gt; /g, " → ");
    codeSpans.push(`<code>${formattedCode}</code>`);
    return `\u0000CODE${idx}\u0000`;
  });

  text = escapeHtml(text);
  text = smartTypography(text);

  text = text.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    (_, label, href) => `<a href="${href}">${label}</a>`
  );
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  text = text.replace(/\u0000CODE(\d+)\u0000/g, (_, idx) => codeSpans[Number(idx)]);
  return text;
}

function parseMarkdown(md) {
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  const htmlParts = [];
  const toc = [];
  let i = 0;
  let currentH3 = "";

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      i++;
      continue;
    }

    // Fenced code blocks & Mermaid upgrades
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const blockLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        blockLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      const content = blockLines.join("\n");

      if (lang === "mermaid" && content.includes("base_link")) {
        htmlParts.push(renderRep105Diagram());
      } else if (lang === "mermaid" && content.includes("predict")) {
        htmlParts.push(renderInteractiveKalmanFigure());
      } else if (lang === "text" && content.startsWith("weight = prediction variance")) {
        htmlParts.push(renderKalmanMathBlock1());
      } else if (lang === "text" && content.includes("updated position = prediction")) {
        htmlParts.push(renderKalmanMathBlock2());
      } else {
        htmlParts.push(`<pre><code>${escapeHtml(content)}</code></pre>`);
      }
      continue;
    }

    // Headings
    const hMatch = line.match(/^(#{1,3})\s+(.*)$/);
    if (hMatch) {
      const depth = hMatch[1].length;
      const rawTitle = hMatch[2].trim();
      const id = slugify(rawTitle);
      if (depth === 3) currentH3 = id;
      if (depth === 2) currentH3 = "";
      if (depth === 2 || depth === 3) {
        toc.push({ depth, id, title: rawTitle.replace(/`([^`]+)`/g, "$1") });
      }
      htmlParts.push(`<h${depth} id="${id}">${formatInline(rawTitle)}</h${depth}>`);
      i++;
      continue;
    }

    // Unordered list
    if (/^-\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^-\s+/.test(lines[i])) {
        items.push(`<li>${formatInline(lines[i].replace(/^-\s+/, ""))}</li>`);
        i++;
      }
      htmlParts.push(`<ul>\n${items.join("\n")}\n</ul>`);
      continue;
    }

    // Ordered list
    if (/^\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
        items.push(`<li>${formatInline(lines[i].replace(/^\d+\.\s+/, ""))}</li>`);
        i++;
      }
      htmlParts.push(`<ol>\n${items.join("\n")}\n</ol>`);
      continue;
    }

    // Paragraph
    const paraLines = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].startsWith("#") &&
      !lines[i].startsWith("```") &&
      !/^-\s+/.test(lines[i]) &&
      !/^\d+\.\s+/.test(lines[i])
    ) {
      paraLines.push(lines[i].trim());
      i++;
    }
    const paraText = paraLines.join(" ");
    htmlParts.push(`<p>${formatInline(paraText)}</p>`);

    // Inject Figure 1 right after introducing LiDAR odometry / ICP
    if (
      currentH3 === "tracking-motion-with-lidar-and-the-arena-walls" &&
      paraText.includes("iterative closest point (ICP)")
    ) {
      htmlParts.push(renderIcpWallDiagram());
    }
  }

  return { bodyHtml: htmlParts.join("\n"), toc };
}

function renderSidebar() {
  const groups = [
    {
      title: "Start here",
      items: [
        { label: "Onboarding", href: "#onboarding" },
        { label: "Set up a Mac", href: "#setup-mac" },
        { label: "Set up Windows with WSL", href: "#setup-windows" },
        { label: "Install ROS 2 on Ubuntu", href: "#setup-ubuntu" },
      ],
    },
    {
      title: "How the rover works",
      items: [
        { label: "System design", href: "#system-design" },
        { label: "Teleop and rover control", href: "#teleop-and-control" },
        { label: "Comms and mission control", href: "#comms" },
        { label: "Sensors", href: "#sensors" },
        { label: "Perception", href: "#perception" },
        { label: "Localisation", href: "./index.html", current: true },
        { label: "Navigation and mission", href: "#navigation-and-mission" },
        { label: "Robot model and simulation", href: "#simulation" },
      ],
    },
    {
      title: "Hardware and bench",
      items: [
        { label: "Rover safety", href: "#safety" },
        { label: "Jetson and router", href: "#jetson" },
        { label: "Teensy drive firmware", href: "#teensy-drive" },
      ],
    },
    {
      title: "Reference",
      items: [
        { label: "Competition rules", href: "#rules" },
        { label: "Drive serial protocol v1", href: "#protocol" },
        { label: "Glossary", href: "#glossary" },
        { label: "Contributing", href: "#contributing" },
      ],
    },
  ];

  return groups
    .map(
      (g) => `
    <div class="nav-group">
      <p class="nav-group-title">${g.title}</p>
      <ul class="nav-list">
        ${g.items
          .map(
            (item) =>
              `<li class="nav-item"><a href="${item.href}"${
                item.current ? ' aria-current="page"' : ""
              }>${item.label}</a></li>`
          )
          .join("\n        ")}
      </ul>
    </div>`
    )
    .join("\n");
}

function buildPage() {
  const md = fs.readFileSync(SOURCE_MD, "utf8");
  const { bodyHtml, toc } = parseMarkdown(md);
  const sidebarHtml = renderSidebar();

  const tocHtml = toc
    .map(
      (item, idx) =>
        `<li class="toc-item depth-${item.depth}"><a href="#${item.id}"${
          idx === 0 ? ' aria-current="location"' : ""
        }>${escapeHtml(item.title)}</a></li>`
    )
    .join("\n          ");

  const html = `<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
  <title>Localisation · INNEX-1 Documentation</title>
  <link rel="stylesheet" href="./styles.css"/>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>

  <header class="topbar">
    <a class="brand" href="./index.html">
      <span>INNEX-1</span>
      <span class="brand-sub">InnovaRobotics · UK Lunabotics 2027</span>
    </a>
    <nav class="topbar-links" aria-label="Project links">
      <a class="topbar-link" href="https://github.com/InnovaRobotics/innex-1">GitHub</a>
      <a class="topbar-link" href="#rules">Rules</a>
      <a class="topbar-link" href="#glossary">Glossary</a>
    </nav>
  </header>

  <details class="mobile-nav">
    <summary>
      <span>Documentation · Localisation</span>
      <span aria-hidden="true">▾</span>
    </summary>
    <nav class="mobile-nav-panel" aria-label="Mobile documentation">
      ${sidebarHtml}
    </nav>
  </details>

  <div class="shell">
    <aside class="sidebar">
      <nav aria-label="Documentation">
        ${sidebarHtml}
      </nav>
    </aside>

    <main id="main-content" class="content-wrap">
      <article class="doc-article">
        ${bodyHtml}
      </article>

      <nav class="doc-pager" aria-label="Page navigation">
        <a class="pager-link prev" href="#perception">
          <span class="pager-dir">Previous</span>
          <span class="pager-title">Perception</span>
        </a>
        <a class="pager-link next" href="#navigation-and-mission">
          <span class="pager-dir">Next</span>
          <span class="pager-title">Navigation and mission</span>
        </a>
      </nav>
    </main>

    <aside class="toc">
      <nav aria-label="On this page">
        <p class="toc-heading">On this page</p>
        <ul class="toc-list">
          ${tocHtml}
        </ul>
      </nav>
    </aside>
  </div>

  <script>
    (() => {
      // Interactive Kalman filter explorer
      const xMin = 1.08;
      const xMax = 2.80;
      const svgX0 = 44;
      const svgX1 = 684;
      const baseY = 194;
      const maxPeakPx = 152;

      const predMean = 2.00;
      const measMean = 1.60;

      const sliderPred = document.getElementById("slider-pred");
      const sliderMeas = document.getElementById("slider-meas");
      const labelPred = document.getElementById("label-pred");
      const labelMeas = document.getElementById("label-meas");
      const outP = document.getElementById("out-p");
      const outR = document.getElementById("out-r");
      const outK = document.getElementById("out-k");
      const outX = document.getElementById("out-x");

      const curvePred = document.getElementById("curve-pred");
      const curveMeas = document.getElementById("curve-meas");
      const curveFused = document.getElementById("curve-fused");
      const curveFusedFill = document.getElementById("curve-fused-fill");
      const lineFusedMean = document.getElementById("line-fused-mean");
      const presetBtns = [...document.querySelectorAll(".preset-btn")];

      function xToPx(x) {
        return svgX0 + ((x - xMin) / (xMax - xMin)) * (svgX1 - svgX0);
      }

      function gaussianPath(mean, sigma, scalePeak, closeFill = false) {
        const steps = 160;
        const pts = [];
        const inv = 1 / (sigma * Math.sqrt(2 * Math.PI));
        for (let i = 0; i <= steps; i++) {
          const x = xMin + (i / steps) * (xMax - xMin);
          const z = (x - mean) / sigma;
          const density = inv * Math.exp(-0.5 * z * z);
          const y = baseY - Math.min(maxPeakPx, density * scalePeak);
          pts.push(\`\${i === 0 ? "M" : "L"} \${xToPx(x).toFixed(1)} \${y.toFixed(1)}\`);
        }
        if (closeFill) {
          pts.push(\`L \${svgX1} \${baseY} L \${svgX0} \${baseY} Z\`);
        }
        return pts.join(" ");
      }

      function updateKalman() {
        if (!sliderPred || !sliderMeas) return;
        const sPred = Number(sliderPred.value);
        const sMeas = Number(sliderMeas.value);
        const P = sPred * sPred;
        const R = sMeas * sMeas;
        const K = P / (P + R);
        const xUpdated = predMean + K * (measMean - predMean);
        const PUpdated = (1 - K) * P;
        const sFused = Math.sqrt(Math.max(PUpdated, 0.0001));

        // Normalise vertical scale so the sharpest curve fits cleanly inside the frame
        const peakDensity = 1 / (Math.max(sFused, 0.045) * Math.sqrt(2 * Math.PI));
        const scalePeak = (maxPeakPx * 0.92) / peakDensity;

        curvePred.setAttribute("d", gaussianPath(predMean, sPred, scalePeak, false));
        curveMeas.setAttribute("d", gaussianPath(measMean, sMeas, scalePeak, false));
        curveFused.setAttribute("d", gaussianPath(xUpdated, sFused, scalePeak, false));
        curveFusedFill.setAttribute("d", gaussianPath(xUpdated, sFused, scalePeak, true));

        const meanPx = xToPx(xUpdated).toFixed(1);
        lineFusedMean.setAttribute("x1", meanPx);
        lineFusedMean.setAttribute("x2", meanPx);

        labelPred.textContent = \`\${sPred.toFixed(2)} m\`;
        labelMeas.textContent = \`\${sMeas.toFixed(2)} m\`;
        outP.textContent = \`\${P.toFixed(3)} m²\`;
        outR.textContent = R >= 1 ? \`\${R.toFixed(2)} m²\` : \`\${R.toFixed(3)} m²\`;
        outK.textContent = K.toFixed(3);
        outX.textContent = \`\${xUpdated.toFixed(2)} m · \${PUpdated.toFixed(3)} m²\`;

        for (const btn of presetBtns) {
          const match =
            Math.abs(Number(btn.dataset.pred) - sPred) < 0.005 &&
            Math.abs(Number(btn.dataset.meas) - sMeas) < 0.005;
          btn.setAttribute("aria-pressed", match ? "true" : "false");
        }
      }

      if (sliderPred && sliderMeas) {
        sliderPred.addEventListener("input", updateKalman);
        sliderMeas.addEventListener("input", updateKalman);
        for (const btn of presetBtns) {
          btn.addEventListener("click", () => {
            sliderPred.value = btn.dataset.pred;
            sliderMeas.value = btn.dataset.meas;
            updateKalman();
          });
        }
        updateKalman();
      }

      // Quiet scroll-spy for "On this page"
      const tocLinks = [...document.querySelectorAll(".toc-item a")];
      const headings = tocLinks
        .map((a) => document.getElementById(a.getAttribute("href").slice(1)))
        .filter(Boolean);

      function updateToc() {
        let activeId = headings[0]?.id;
        for (const h of headings) {
          if (h.getBoundingClientRect().top <= 110) {
            activeId = h.id;
          }
        }
        for (const a of tocLinks) {
          if (a.getAttribute("href") === \`#\${activeId}\`) {
            a.setAttribute("aria-current", "location");
          } else {
            a.removeAttribute("aria-current");
          }
        }
      }

      window.addEventListener("scroll", updateToc, { passive: true });
      updateToc();
    })();
  </script>
</body>
</html>`;

  fs.mkdirSync(DIST_DIR, { recursive: true });
  fs.writeFileSync(path.join(DIST_DIR, "index.html"), html, "utf8");
  fs.copyFileSync(path.join(__dirname, "styles.css"), path.join(DIST_DIR, "styles.css"));
  console.log(`Built ${path.join(DIST_DIR, "index.html")} from ${SOURCE_MD}`);
}

buildPage();

if (process.argv.includes("--serve")) {
  const port = Number(process.env.PORT || 4321);
  const mime = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".js": "text/javascript; charset=utf-8",
  };
  const server = http.createServer((req, res) => {
    // Rebuild on each HTML request so edits to localisation.md or styles.css appear immediately on reload
    const urlPath = (req.url || "/").split("?")[0];
    if (urlPath === "/" || urlPath === "/index.html") {
      buildPage();
    }
    const rel = urlPath === "/" ? "index.html" : urlPath.replace(/^\/+/, "");
    const filePath = path.join(DIST_DIR, rel);
    if (!filePath.startsWith(DIST_DIR) || !fs.existsSync(filePath)) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { "Content-Type": mime[ext] || "application/octet-stream" });
    res.end(fs.readFileSync(filePath));
  });
  server.listen(port, "127.0.0.1", () => {
    console.log(`Serving INNEX-1 docs preview on http://127.0.0.1:${port}`);
  });
}
