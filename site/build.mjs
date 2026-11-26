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
  renderPositiveNegativeObstaclesDiagram,
  renderMissionCycleDiagram,
  renderHardwareConnectionsDiagram,
  renderSubsystemLoopDiagram,
} from "./diagrams.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");
const DIST_DIR = path.join(__dirname, "dist");
const FONTS_DIR = path.join(__dirname, "fonts");

const EXCLUDED_DOCS = new Set(["docs/sdr.md", "docs/software-sdr.md"]);

const SYSTEM_ORDER = [
  "docs/system-design.md",
  "docs/system/teleop-and-control.md",
  "docs/system/comms.md",
  "docs/system/sensors.md",
  "docs/system/perception.md",
  "docs/system/localisation.md",
  "docs/system/navigation-and-mission.md",
  "docs/system/simulation.md",
];

const START_ORDER = [
  "README.md",
  "ONBOARDING.md",
  "docs/setup-mac.md",
  "docs/setup-windows.md",
  "docs/setup-ubuntu.md",
];

const BENCH_ORDER = ["docs/safety.md", "docs/jetson.md"];

const REF_ORDER = [
  "docs/rules.md",
  "docs/glossary.md",
  "CONTRIBUTING.md",
  "REVIEW.md",
  "AGENTS.md",
];

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

function extractTitle(md, fallback) {
  const m = md.match(/^#\s+(.+)$/m);
  if (!m) return fallback;
  const raw = m[1].replace(/`([^`]+)`/g, "$1").trim();
  if (raw === "INNEX-1") return "Overview";
  return raw;
}

function repoRelToOutRel(repoRel) {
  if (repoRel === "README.md") return "index.html";
  if (!repoRel.includes("/")) {
    return `${repoRel.replace(/\.md$/i, "").toLowerCase()}.html`;
  }
  if (repoRel.startsWith("docs/")) {
    return repoRel.replace(/\.md$/i, ".html");
  }
  // src/<pkg>/README.md or firmware/<pkg>/PROTOCOL.md
  const parts = repoRel.split("/");
  const base = parts[parts.length - 1];
  const stem = base.toLowerCase() === "readme.md" ? "index" : base.replace(/\.md$/i, "").toLowerCase();
  return path.posix.join("packages", ...parts.slice(1, -1), `${stem}.html`);
}

function discoverDocs() {
  const found = new Set();

  for (const rootFile of ["README.md", "ONBOARDING.md", "CONTRIBUTING.md", "REVIEW.md", "AGENTS.md"]) {
    if (fs.existsSync(path.join(REPO_ROOT, rootFile))) found.add(rootFile);
  }

  // Scan docs/ and docs/system/ dynamically so any newly added or uploaded .md file appears automatically
  function scanDir(relDir) {
    const abs = path.join(REPO_ROOT, relDir);
    if (!fs.existsSync(abs)) return;
    for (const entry of fs.readdirSync(abs, { withFileTypes: true })) {
      const childRel = path.posix.join(relDir, entry.name);
      if (entry.isDirectory()) {
        scanDir(childRel);
      } else if (entry.isFile() && entry.name.endsWith(".md") && !EXCLUDED_DOCS.has(childRel)) {
        found.add(childRel);
      }
    }
  }
  scanDir("docs");

  // Scan src/*/ and firmware/*/ for package READMEs and protocol specs
  for (const parentDir of ["src", "firmware"]) {
    const absParent = path.join(REPO_ROOT, parentDir);
    if (!fs.existsSync(absParent)) continue;
    for (const pkg of fs.readdirSync(absParent, { withFileTypes: true })) {
      if (!pkg.isDirectory()) continue;
      const pkgRel = path.posix.join(parentDir, pkg.name);
      for (const f of fs.readdirSync(path.join(REPO_ROOT, pkgRel), { withFileTypes: true })) {
        if (f.isFile() && f.name.endsWith(".md")) {
          found.add(path.posix.join(pkgRel, f.name));
        }
      }
    }
  }

  const assigned = new Set();
  function takeOrdered(preferredList, filterFn) {
    const items = [];
    for (const rel of preferredList) {
      if (found.has(rel) && !assigned.has(rel)) {
        items.push(rel);
        assigned.add(rel);
      }
    }
    const extras = [...found]
      .filter((rel) => !assigned.has(rel) && filterFn(rel))
      .sort();
    for (const rel of extras) {
      items.push(rel);
      assigned.add(rel);
    }
    return items;
  }

  const startItems = takeOrdered(START_ORDER, (r) => r.startsWith("docs/setup-"));
  const systemItems = takeOrdered(SYSTEM_ORDER, (r) => r.startsWith("docs/system/"));
  const benchItems = takeOrdered(BENCH_ORDER, () => false);
  const packageItems = takeOrdered(
    [
      "src/innex_description/README.md",
      "src/innex_sim/README.md",
      "src/innex_teleop/README.md",
      "src/innex_drive_bridge/README.md",
      "src/innex_video/README.md",
      "firmware/teensy_drive/README.md",
      "firmware/teensy_drive/PROTOCOL.md",
    ],
    (r) => r.startsWith("src/") || r.startsWith("firmware/")
  );
  // Any remaining unassigned docs/ files land automatically in Reference (or Docs)
  const refItems = takeOrdered(REF_ORDER, () => true);

  const groups = [
    { title: "Start here", files: startItems },
    { title: "How the rover works", files: systemItems },
    { title: "Hardware and bench", files: benchItems },
    { title: "Packages and firmware", files: packageItems },
    { title: "Reference", files: refItems },
  ].filter((g) => g.files.length > 0);

  const pageMap = new Map();
  const flatOrder = [];

  for (const group of groups) {
    group.pages = group.files.map((repoRel) => {
      const md = fs.readFileSync(path.join(REPO_ROOT, repoRel), "utf8");
      const outRel = repoRelToOutRel(repoRel);
      const fallback = path.basename(repoRel, ".md");
      const label =
        repoRel === "firmware/teensy_drive/PROTOCOL.md"
          ? "teensy_drive protocol"
          : extractTitle(md, fallback);
      const page = { repoRel, outRel, label, groupTitle: group.title, md };
      pageMap.set(repoRel, page);
      flatOrder.push(page);
      return page;
    });
  }

  return { groups, pageMap, flatOrder };
}

function relativeHref(fromOutRel, toOutRel) {
  const fromDir = path.posix.dirname(fromOutRel);
  let rel = path.posix.relative(fromDir === "." ? "" : fromDir, toOutRel);
  if (!rel.startsWith(".")) rel = `./${rel}`;
  return rel;
}

function resolveDocHref(rawHref, currentPage, pageMap) {
  if (/^(https?:|mailto:|#)/i.test(rawHref)) return rawHref;
  const [relPart, hashPart] = rawHref.split("#");
  const curDir = path.posix.dirname(currentPage.repoRel);
  const resolvedRepoRel = path.posix.normalize(
    curDir === "." ? relPart : path.posix.join(curDir, relPart)
  );
  const targetPage = pageMap.get(resolvedRepoRel);
  if (!targetPage) return rawHref;
  const href = relativeHref(currentPage.outRel, targetPage.outRel);
  return hashPart ? `${href}#${hashPart}` : href;
}

function formatInline(raw, currentPage, pageMap) {
  const codeSpans = [];
  const plainMeasurementRe =
    /^-?\d+(?:\.\d+)?\s*(?:m|cm|mm)?(?:\s*(?:x|×|\/|\*|=|-)\s*-?\d+(?:\.\d+)?\s*(?:m|cm|mm)?)?\s*(?:m|cm|mm|ms|s|W|Wh|kg|Hz|kbps|degrees?|per cent|m\^2)?$/i;

  let text = raw.replace(/`([^`]+)`/g, (_, code) => {
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

  // Auto-link bare <https://...> angle-bracket URLs
  text = text.replace(/<(https?:\/\/[^>]+)>/g, "[$1]($1)");

  text = escapeHtml(text);
  text = smartTypography(text);

  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    const resolved = resolveDocHref(href, currentPage, pageMap);
    return `<a href="${resolved}">${label}</a>`;
  });
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  text = text.replace(/\u0000CODE(\d+)\u0000/g, (_, idx) => codeSpans[Number(idx)]);
  return text;
}

function parseTableRow(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((c) => c.trim());
}

function parseListBlock(lines, startIdx, ordered, currentPage, pageMap) {
  const itemMarkerRe = ordered ? /^\s*\d+\.\s+(.*)$/ : /^\s*-\s+(.*)$/;
  const items = [];
  let i = startIdx;

  while (i < lines.length) {
    const m = lines[i].match(itemMarkerRe);
    if (!m) break;

    const itemParts = [`<p>${formatInline(m[1].trim(), currentPage, pageMap)}</p>`];
    i++;

    while (i < lines.length) {
      const cur = lines[i];
      if (!cur.trim()) {
        // Look ahead to see if indented continuation or next list item follows
        if (i + 1 < lines.length && (/^\s{2,}/.test(lines[i + 1]) || itemMarkerRe.test(lines[i + 1]))) {
          i++;
          continue;
        }
        break;
      }
      if (itemMarkerRe.test(cur) || /^#{1,4}\s+/.test(cur)) break;

      if (/^\s{2,}```/.test(cur)) {
        const block = [];
        i++;
        while (i < lines.length && !/^\s*```/.test(lines[i])) {
          block.push(lines[i].replace(/^\s{2,4}/, ""));
          i++;
        }
        i++;
        itemParts.push(`<pre><code>${escapeHtml(block.join("\n"))}</code></pre>`);
        continue;
      }

      if (/^\s{2,}-\s+/.test(cur) || /^\s{2,}[a-z]\.\s+/.test(cur)) {
        const subOrdered = /^\s{2,}[a-z]\.\s+/.test(cur);
        const subRe = subOrdered ? /^\s{2,}[a-z]\.\s+(.*)$/ : /^\s{2,}-\s+(.*)$/;
        const subItems = [];
        while (i < lines.length && subRe.test(lines[i])) {
          const sm = lines[i].match(subRe);
          subItems.push(`<li>${formatInline(sm[1].trim(), currentPage, pageMap)}</li>`);
          i++;
        }
        const tag = subOrdered ? "ol" : "ul";
        itemParts.push(`<${tag}>${subItems.join("")}</${tag}>`);
        continue;
      }

      if (/^\s{2,}/.test(cur)) {
        const cont = [];
        while (
          i < lines.length &&
          lines[i].trim() &&
          /^\s{2,}/.test(lines[i]) &&
          !/^\s{2,}```/.test(lines[i]) &&
          !/^\s{2,}-\s+/.test(lines[i])
        ) {
          cont.push(lines[i].trim());
          i++;
        }
        itemParts.push(`<p>${formatInline(cont.join(" "), currentPage, pageMap)}</p>`);
        continue;
      }

      break;
    }

    // Simplify single-paragraph list items so spacing stays compact
    if (itemParts.length === 1 && itemParts[0].startsWith("<p>")) {
      items.push(`<li>${itemParts[0].slice(3, -4)}</li>`);
    } else {
      items.push(`<li>${itemParts.join("\n")}</li>`);
    }
  }

  const tag = ordered ? "ol" : "ul";
  return { html: `<${tag}>\n${items.join("\n")}\n</${tag}>`, nextIdx: i };
}

function parseMarkdown(md, currentPage, pageMap) {
  const cleaned = md.replace(/<!--[\s\S]*?-->/g, "").replace(/\r\n/g, "\n");
  const lines = cleaned.split("\n");
  const htmlParts = [];
  const tocSections = [];
  let currentH2Section = null;
  let currentH3 = "";
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      i++;
      continue;
    }

    // Fenced code / diagram blocks
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const blockLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        blockLines.push(lines[i]);
        i++;
      }
      i++;
      const content = blockLines.join("\n");

      if (lang === "mermaid") {
        if (currentPage.repoRel === "docs/system/localisation.md" && content.includes("base_link")) {
          htmlParts.push(renderRep105Diagram());
        } else if (currentPage.repoRel === "docs/system/localisation.md" && content.includes("predict")) {
          htmlParts.push(renderInteractiveKalmanFigure());
        } else if (currentPage.repoRel === "docs/system/navigation-and-mission.md") {
          htmlParts.push(renderMissionCycleDiagram());
        } else if (currentPage.repoRel === "docs/system-design.md" && content.includes("sabertooth")) {
          htmlParts.push(renderHardwareConnectionsDiagram());
        } else if (currentPage.repoRel === "docs/system-design.md") {
          htmlParts.push(renderSubsystemLoopDiagram());
        } else {
          htmlParts.push(`<pre><code>${escapeHtml(content)}</code></pre>`);
        }
      } else if (
        currentPage.repoRel === "docs/system/localisation.md" &&
        content.startsWith("weight = prediction variance")
      ) {
        htmlParts.push(renderKalmanMathBlock1());
      } else if (
        currentPage.repoRel === "docs/system/localisation.md" &&
        content.includes("updated position = prediction")
      ) {
        htmlParts.push(renderKalmanMathBlock2());
      } else if (
        currentPage.repoRel === "docs/system/perception.md" &&
        content.includes("Boulder") &&
        content.includes("Crater")
      ) {
        htmlParts.push(renderPositiveNegativeObstaclesDiagram());
      } else {
        htmlParts.push(`<pre><code>${escapeHtml(content)}</code></pre>`);
      }
      continue;
    }

    // Tables
    if (line.trim().startsWith("|") && i + 1 < lines.length && /^\s*\|[\s:-]+\|/.test(lines[i + 1])) {
      const headers = parseTableRow(lines[i]);
      i += 2;
      const bodyRows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        bodyRows.push(parseTableRow(lines[i]));
        i++;
      }
      const thead = `<thead><tr>${headers
        .map((h) => `<th>${formatInline(h, currentPage, pageMap)}</th>`)
        .join("")}</tr></thead>`;
      const tbody = `<tbody>${bodyRows
        .map(
          (row) =>
            `<tr>${row
              .map((cell) => `<td>${formatInline(cell, currentPage, pageMap)}</td>`)
              .join("")}</tr>`
        )
        .join("")}</tbody>`;
      htmlParts.push(`<div class="table-wrap"><table>${thead}${tbody}</table></div>`);
      continue;
    }

    // Blockquotes
    if (line.startsWith(">")) {
      const qLines = [];
      while (i < lines.length && lines[i].startsWith(">")) {
        qLines.push(lines[i].replace(/^>\s?/, ""));
        i++;
      }
      const inner = parseMarkdown(qLines.join("\n"), currentPage, pageMap).bodyHtml;
      htmlParts.push(`<blockquote class="math-block">${inner}</blockquote>`);
      continue;
    }

    // Headings
    const hMatch = line.match(/^(#{1,4})\s+(.*)$/);
    if (hMatch) {
      const depth = Math.min(3, hMatch[1].length);
      const rawTitle = hMatch[2].trim();
      const id = slugify(rawTitle);
      const cleanTitle = rawTitle.replace(/`([^`]+)`/g, "$1");

      if (hMatch[1].length === 2) {
        currentH2Section = { id, title: cleanTitle, children: [] };
        tocSections.push(currentH2Section);
        currentH3 = "";
      } else if (hMatch[1].length === 3) {
        currentH3 = id;
        if (currentH2Section) {
          currentH2Section.children.push({ id, title: cleanTitle });
        }
      }
      htmlParts.push(`<h${depth} id="${id}">${formatInline(rawTitle, currentPage, pageMap)}</h${depth}>`);
      i++;
      continue;
    }

    // Lists
    if (/^\s*-\s+/.test(line)) {
      const { html, nextIdx } = parseListBlock(lines, i, false, currentPage, pageMap);
      htmlParts.push(html);
      i = nextIdx;
      continue;
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      const { html, nextIdx } = parseListBlock(lines, i, true, currentPage, pageMap);
      htmlParts.push(html);
      i = nextIdx;
      continue;
    }

    // Paragraph
    const paraLines = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].startsWith("#") &&
      !lines[i].startsWith("```") &&
      !lines[i].startsWith(">") &&
      !(lines[i].trim().startsWith("|") && i + 1 < lines.length && /^\s*\|[\s:-]+\|/.test(lines[i + 1])) &&
      !/^\s*-\s+/.test(lines[i]) &&
      !/^\s*\d+\.\s+/.test(lines[i])
    ) {
      paraLines.push(lines[i].trim());
      i++;
    }
    const paraText = paraLines.join(" ");
    htmlParts.push(`<p>${formatInline(paraText, currentPage, pageMap)}</p>`);

    if (
      currentPage.repoRel === "docs/system/localisation.md" &&
      currentH3 === "lidar-odometry" &&
      paraText.includes("iterative closest point (ICP)")
    ) {
      htmlParts.push(renderIcpWallDiagram());
    }
  }

  return { bodyHtml: htmlParts.join("\n"), tocSections };
}

function renderSidebar(groups, currentPage) {
  const chevronSvg = `<svg class="group-chevron" viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3.5L10.5 8L6 12.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

  return groups
    .map((group) => {
      const containsCurrent = group.pages.some((p) => p.repoRel === currentPage.repoRel);
      const openAttr =
        containsCurrent || group.title === "Start here" || group.title === "How the rover works"
          ? " open"
          : "";
      const links = group.pages
        .map((p) => {
          const href = relativeHref(currentPage.outRel, p.outRel);
          const currentAttr = p.repoRel === currentPage.repoRel ? ' aria-current="page"' : "";
          return `<li class="nav-item"><a href="${href}"${currentAttr}>${escapeHtml(p.label)}</a></li>`;
        })
        .join("\n          ");

      return `
      <details class="nav-group"${openAttr}>
        <summary>
          <span>${escapeHtml(group.title)}</span>
          ${chevronSvg}
        </summary>
        <ul class="nav-list">
          ${links}
        </ul>
      </details>`;
    })
    .join("\n");
}

function renderToc(tocSections, pageLabel) {
  if (tocSections.length === 0) return "";
  const chevron = `<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M4.2 2.5L7.8 6L4.2 9.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

  const items = tocSections
    .map((sec, idx) => {
      const hasChildren = sec.children.length > 0;
      const openClass = idx === 0 && hasChildren ? " is-open" : "";
      const toggleBtn = hasChildren
        ? `<button type="button" class="toc-toggle" aria-label="Toggle ${escapeHtml(sec.title)} subsections">${chevron}</button>`
        : "";
      const childrenHtml = hasChildren
        ? `<div class="toc-sublist-wrap"><ul class="toc-sublist">${sec.children
            .map(
              (c) =>
                `<li><a class="toc-link" href="#${c.id}">${escapeHtml(c.title)}</a></li>`
            )
            .join("")}</ul></div>`
        : "";

      return `
          <li class="toc-section${hasChildren ? " has-children" : ""}${openClass}" data-section-id="${sec.id}">
            <div class="toc-row">
              ${toggleBtn}
              <a class="toc-link" href="#${sec.id}"${idx === 0 ? ' aria-current="location"' : ""}>${escapeHtml(sec.title)}</a>
            </div>
            ${childrenHtml}
          </li>`;
    })
    .join("");

  return `
    <aside class="toc">
      <nav aria-label="On this page">
        <p class="toc-doc-title">${escapeHtml(pageLabel)}</p>
        <ul class="toc-list" id="toc-list">
          <li class="toc-dot" id="toc-dot" aria-hidden="true"></li>
          ${items}
        </ul>
      </nav>
    </aside>`;
}

function copyStaticAssets() {
  fs.mkdirSync(DIST_DIR, { recursive: true });
  fs.copyFileSync(path.join(__dirname, "styles.css"), path.join(DIST_DIR, "styles.css"));
  const distFonts = path.join(DIST_DIR, "fonts");
  fs.mkdirSync(distFonts, { recursive: true });
  if (fs.existsSync(FONTS_DIR)) {
    for (const f of fs.readdirSync(FONTS_DIR)) {
      fs.copyFileSync(path.join(FONTS_DIR, f), path.join(distFonts, f));
    }
  }
}

function buildAllPages() {
  copyStaticAssets();
  const { groups, pageMap, flatOrder } = discoverDocs();

  flatOrder.forEach((page, idx) => {
    const { bodyHtml, tocSections } = parseMarkdown(page.md, page, pageMap);
    const sidebarHtml = renderSidebar(groups, page);
    const tocHtml = renderToc(tocSections, page.label);

    const cssHref = relativeHref(page.outRel, "styles.css");
    const homeHref = relativeHref(page.outRel, "index.html");
    const rulesHref = relativeHref(page.outRel, "docs/rules.html");
    const glossaryHref = relativeHref(page.outRel, "docs/glossary.html");

    const prevPage = idx > 0 ? flatOrder[idx - 1] : null;
    const nextPage = idx < flatOrder.length - 1 ? flatOrder[idx + 1] : null;

    const pagerHtml = `
      <nav class="doc-pager" aria-label="Page navigation">
        ${
          prevPage
            ? `<a class="pager-link prev" href="${relativeHref(page.outRel, prevPage.outRel)}">
                <span class="pager-dir">Previous</span>
                <span class="pager-title">${escapeHtml(prevPage.label)}</span>
              </a>`
            : "<span></span>"
        }
        ${
          nextPage
            ? `<a class="pager-link next" href="${relativeHref(page.outRel, nextPage.outRel)}">
                <span class="pager-dir">Next</span>
                <span class="pager-title">${escapeHtml(nextPage.label)}</span>
              </a>`
            : ""
        }
      </nav>`;

    const html = `<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
  <title>${escapeHtml(page.label)} · INNEX-1</title>
  <link rel="stylesheet" href="${cssHref}"/>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to content</a>

  <header class="topbar">
    <a class="brand" href="${homeHref}">
      <span>INNEX-1</span>
      <span class="brand-sub">InnovaRobotics · UK Lunabotics 2027</span>
    </a>
    <nav class="topbar-links" aria-label="Project links">
      <a class="topbar-link" href="${rulesHref}">Rules</a>
      <a class="topbar-link" href="${glossaryHref}">Glossary</a>
      <a class="topbar-link" href="https://github.com/InnovaRobotics/innex-1">GitHub</a>
    </nav>
  </header>

  <details class="mobile-nav">
    <summary>
      <span>${escapeHtml(page.groupTitle)} · ${escapeHtml(page.label)}</span>
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
      ${pagerHtml}
    </main>

    ${tocHtml}
  </div>

  <script>
    (() => {
      const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

      // 1. Wikiwand-style right TOC with gliding active dot and collapsible subsections
      const tocList = document.getElementById("toc-list");
      const tocDot = document.getElementById("toc-dot");
      const tocLinks = [...document.querySelectorAll(".toc-link")];
      const tocSections = [...document.querySelectorAll(".toc-section")];

      for (const sec of tocSections) {
        const btn = sec.querySelector(".toc-toggle");
        if (btn) {
          btn.addEventListener("click", (e) => {
            e.preventDefault();
            sec.classList.toggle("is-open");
            requestAnimationFrame(positionDot);
          });
        }
      }

      const trackedHeadings = tocLinks
        .map((a) => ({
          link: a,
          el: document.getElementById(a.getAttribute("href").slice(1)),
          section: a.closest(".toc-section"),
        }))
        .filter((x) => x.el);

      function positionDot() {
        if (!tocList || !tocDot) return;
        const activeLink = tocList.querySelector('.toc-link[aria-current="location"]');
        if (!activeLink) return;
        const listRect = tocList.getBoundingClientRect();
        const linkRect = activeLink.getBoundingClientRect();
        const y = linkRect.top - listRect.top + linkRect.height / 2 - 2.5;
        tocDot.style.transform = \`translateY(\${y.toFixed(1)}px)\`;
        tocDot.classList.add("is-ready");
      }

      function updateTocOnScroll() {
        if (!trackedHeadings.length) return;
        let current = trackedHeadings[0];
        for (const item of trackedHeadings) {
          if (item.el.getBoundingClientRect().top <= 124) {
            current = item;
          }
        }
        for (const item of trackedHeadings) {
          if (item === current) {
            item.link.setAttribute("aria-current", "location");
          } else {
            item.link.removeAttribute("aria-current");
          }
        }
        for (const sec of tocSections) {
          const isActiveSec = sec === current.section;
          sec.classList.toggle("is-active", isActiveSec && current.link.parentElement.classList.contains("toc-row"));
          if (isActiveSec && sec.classList.contains("has-children")) {
            sec.classList.add("is-open");
          }
        }
        positionDot();
      }

      if (trackedHeadings.length) {
        window.addEventListener("scroll", updateTocOnScroll, { passive: true });
        window.addEventListener("resize", positionDot, { passive: true });
        if (document.fonts && document.fonts.ready) {
          document.fonts.ready.then(updateTocOnScroll);
        }
        updateTocOnScroll();
      }

      // 2. Interactive Kalman filter explorer with smooth interruptible ease-out transitions
      const sliderPred = document.getElementById("slider-pred");
      const sliderMeas = document.getElementById("slider-meas");
      if (!sliderPred || !sliderMeas) return;

      const xMin = 1.08;
      const xMax = 2.80;
      const svgX0 = 36;
      const svgX1 = 664;
      const baseY = 188;
      const maxPeakPx = 148;
      const predMean = 2.00;
      const measMean = 1.60;

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
      const indicator = document.getElementById("preset-indicator");

      let animState = { sPred: 0.30, sMeas: 0.10 };
      let rafId = 0;

      // Strong ease-out matching --ease-out: cubic-bezier(0.23, 1, 0.32, 1)
      function easeOutStrong(t) {
        return 1 - Math.pow(1 - t, 3.6);
      }

      function xToPx(x) {
        return svgX0 + ((x - xMin) / (xMax - xMin)) * (svgX1 - svgX0);
      }

      function gaussianPath(mean, sigma, scalePeak, closeFill) {
        const steps = 160;
        const pts = [];
        const inv = 1 / (sigma * Math.sqrt(2 * Math.PI));
        for (let k = 0; k <= steps; k++) {
          const x = xMin + (k / steps) * (xMax - xMin);
          const z = (x - mean) / sigma;
          const density = inv * Math.exp(-0.5 * z * z);
          const y = baseY - Math.min(maxPeakPx, density * scalePeak);
          pts.push(\`\${k === 0 ? "M" : "L"} \${xToPx(x).toFixed(1)} \${y.toFixed(1)}\`);
        }
        if (closeFill) {
          pts.push(\`L \${svgX1} \${baseY} L \${svgX0} \${baseY} Z\`);
        }
        return pts.join(" ");
      }

      function syncPresetIndicator() {
        if (!indicator) return;
        const activeBtn = presetBtns.find((b) => b.getAttribute("aria-pressed") === "true");
        if (!activeBtn) {
          indicator.style.opacity = "0";
          return;
        }
        indicator.style.opacity = "1";
        indicator.style.width = \`\${activeBtn.offsetWidth}px\`;
        indicator.style.transform = \`translateX(\${activeBtn.offsetLeft}px)\`;
      }

      function renderKalmanValues(sPred, sMeas) {
        animState.sPred = sPred;
        animState.sMeas = sMeas;

        const P = sPred * sPred;
        const R = sMeas * sMeas;
        const K = P / (P + R);
        const xUpdated = predMean + K * (measMean - predMean);
        const PUpdated = (1 - K) * P;
        const sFused = Math.sqrt(Math.max(PUpdated, 0.0001));

        const peakDensity = 1 / (Math.max(sFused, 0.045) * Math.sqrt(2 * Math.PI));
        const scalePeak = (maxPeakPx * 0.9) / peakDensity;

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
        outK.textContent = K < 0.01 ? K.toFixed(3) : K.toFixed(2);
        outX.textContent = \`\${xUpdated.toFixed(2)} m (±\${sFused.toFixed(2)} m)\`;
      }

      function markMatchingPreset(targetPred, targetMeas) {
        for (const btn of presetBtns) {
          const match =
            Math.abs(Number(btn.dataset.pred) - targetPred) < 0.005 &&
            Math.abs(Number(btn.dataset.meas) - targetMeas) < 0.005;
          btn.setAttribute("aria-pressed", match ? "true" : "false");
        }
        syncPresetIndicator();
      }

      function animateTo(targetPred, targetMeas) {
        cancelAnimationFrame(rafId);
        markMatchingPreset(targetPred, targetMeas);

        if (reducedMotion()) {
          sliderPred.value = targetPred.toFixed(2);
          sliderMeas.value = targetMeas.toFixed(2);
          renderKalmanValues(targetPred, targetMeas);
          return;
        }

        const startPred = animState.sPred;
        const startMeas = animState.sMeas;
        const duration = 280;
        const t0 = performance.now();

        function tick(now) {
          const elapsed = now - t0;
          const p = Math.min(1, elapsed / duration);
          const e = easeOutStrong(p);
          const curPred = startPred + (targetPred - startPred) * e;
          const curMeas = startMeas + (targetMeas - startMeas) * e;

          sliderPred.value = curPred.toFixed(2);
          sliderMeas.value = curMeas.toFixed(2);
          renderKalmanValues(curPred, curMeas);

          if (p < 1) {
            rafId = requestAnimationFrame(tick);
          }
        }
        rafId = requestAnimationFrame(tick);
      }

      sliderPred.addEventListener("input", () => {
        cancelAnimationFrame(rafId);
        const sp = Number(sliderPred.value);
        const sm = Number(sliderMeas.value);
        markMatchingPreset(sp, sm);
        renderKalmanValues(sp, sm);
      });

      sliderMeas.addEventListener("input", () => {
        cancelAnimationFrame(rafId);
        const sp = Number(sliderPred.value);
        const sm = Number(sliderMeas.value);
        markMatchingPreset(sp, sm);
        renderKalmanValues(sp, sm);
      });

      for (const btn of presetBtns) {
        btn.addEventListener("click", () => {
          animateTo(Number(btn.dataset.pred), Number(btn.dataset.meas));
        });
      }

      renderKalmanValues(0.30, 0.10);
      requestAnimationFrame(syncPresetIndicator);
      window.addEventListener("resize", syncPresetIndicator, { passive: true });
    })();
  </script>
</body>
</html>`;

    const destPath = path.join(DIST_DIR, page.outRel);
    fs.mkdirSync(path.dirname(destPath), { recursive: true });
    fs.writeFileSync(destPath, html, "utf8");
  });

  return flatOrder.length;
}

const count = buildAllPages();
console.log(`Built ${count} documentation pages into ${DIST_DIR}`);

if (process.argv.includes("--serve")) {
  const port = Number(process.env.PORT || 4321);
  const mime = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".js": "text/javascript; charset=utf-8",
    ".woff2": "font/woff2",
  };
  const server = http.createServer((req, res) => {
    const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
    if (urlPath.endsWith(".html") || urlPath === "/" || urlPath.endsWith("/")) {
      buildAllPages();
    }
    let rel = urlPath.replace(/^\/+/, "");
    if (!rel || rel.endsWith("/")) rel = path.posix.join(rel, "index.html");
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
    console.log(`Serving all INNEX-1 docs on http://127.0.0.1:${port}`);
  });
}
