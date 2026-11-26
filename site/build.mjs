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
  renderCostmapInflationDiagram,
  renderSerialPacketDiagram,
  renderSkidSteerMathBlock,
  renderOusterMathBlock,
  renderInteractiveOusterFigure,
} from "./diagrams.mjs";
import { GLOSSARY_VISUALS } from "./glossary-visuals.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");
const DIST_DIR = path.join(__dirname, "dist");
const FONTS_DIR = path.join(__dirname, "fonts");
const IMAGES_DIR = path.join(__dirname, "images");

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

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
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
  const parts = repoRel.split("/");
  const base = parts[parts.length - 1];
  const stem =
    base.toLowerCase() === "readme.md" ? "index" : base.replace(/\.md$/i, "").toLowerCase();
  return path.posix.join("packages", ...parts.slice(1, -1), `${stem}.html`);
}

function parseGlossaryCatalogue() {
  const glossaryPath = path.join(REPO_ROOT, "docs/glossary.md");
  const raw = fs.readFileSync(glossaryPath, "utf8").replace(/\r\n/g, "\n");
  const sections = raw.split(/^##\s+/m).slice(1);

  const entries = {};
  const matchers = [];

  for (const sec of sections) {
    const lines = sec.split("\n");
    const title = lines[0].trim();
    const slug = slugify(title);
    let subtitle = "";
    const aliases = [];

    let bodyStart = 1;
    for (let k = 1; k < lines.length; k++) {
      const trimmed = lines[k].trim();
      if (!trimmed) continue;
      const metaMatch = trimmed.match(/^<!--\s*(.*?)\s*-->$/);
      if (metaMatch) {
        const parts = metaMatch[1].split("|").map((s) => s.trim());
        for (const p of parts) {
          if (p.startsWith("subtitle:")) {
            subtitle = p.slice("subtitle:".length).trim();
          } else if (p.startsWith("aliases:")) {
            for (const a of p.slice("aliases:".length).split(",")) {
              if (a.trim()) aliases.push(a.trim());
            }
          }
        }
        bodyStart = k + 1;
      }
      break;
    }

    const rawBody = lines
      .slice(bodyStart)
      .join(" ")
      .replace(/<!--[\s\S]*?-->/g, "")
      .replace(/\s+/g, " ")
      .trim();

    // Extract first external https:// link if present for the card footer
    let extUrl = "";
    let extLabel = "";
    for (const lm of rawBody.matchAll(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g)) {
      extLabel = lm[1].replace(/`([^`]+)`/g, "$1").trim();
      extUrl = lm[2].trim();
      break;
    }

    // Strip trailing "See ..." cross-reference sentence from the compact card summary
    let summaryMd = rawBody.replace(/\s*See\s+\[[^\n]+$/, "").trim();
    if (subtitle) {
      const leadPrefix = new RegExp(`^${escapeRegex(subtitle)},\\s+`, "i");
      if (leadPrefix.test(summaryMd)) {
        summaryMd = summaryMd.replace(leadPrefix, "");
        summaryMd = summaryMd.charAt(0).toUpperCase() + summaryMd.slice(1);
      }
    }
    const codeSpans = [];
    let summaryHtml = summaryMd.replace(/`([^`]+)`/g, (_, c) => {
      const idx = codeSpans.length;
      codeSpans.push(`<code>${escapeHtml(c)}</code>`);
      return `\u0000C${idx}\u0000`;
    });
    summaryHtml = summaryHtml.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
    summaryHtml = smartTypography(escapeHtml(summaryHtml));
    summaryHtml = summaryHtml.replace(/\u0000C(\d+)\u0000/g, (_, idx) => codeSpans[Number(idx)]);

    entries[slug] = {
      slug,
      title,
      subtitle,
      bodyHtml: summaryHtml,
      visual: GLOSSARY_VISUALS[slug] || "",
      extUrl,
      extLabel,
    };

    const candidatePhrases = new Set([title, ...aliases]);
    for (const phrase of [...candidatePhrases]) {
      // Add simple plural for regular multi-letter English nouns
      if (/^[A-Za-z][a-z]{3,}$/.test(phrase) && !phrase.endsWith("s")) {
        candidatePhrases.add(`${phrase}s`);
      }
    }

    for (const phrase of candidatePhrases) {
      // Skip ambiguous bare nouns (both singular and plural) so "serial frames" or "commit messages" never false-match
      if (/^(actions?|nodes?|messages?|topics?|frames?|bridges?)$/i.test(phrase)) {
        continue;
      }
      const isCaseSensitive = /^[A-Z0-9\s-]{2,8}$/.test(phrase) || phrase === "LiDAR";
      const flags = isCaseSensitive ? "g" : "gi";
      const regex = new RegExp(`(?<![\\w/-])(${escapeRegex(phrase)})(?![\\w/-])`, flags);
      matchers.push({ slug, phrase, length: phrase.length, regex });
    }
  }

  // Match longest phrases first ("LiDAR odometry" before "LiDAR" or "odometry")
  matchers.sort((a, b) => b.length - a.length);
  return { entries, matchers };
}

function discoverDocs() {
  const found = new Set();

  for (const rootFile of ["README.md", "ONBOARDING.md", "CONTRIBUTING.md", "REVIEW.md", "AGENTS.md"]) {
    if (fs.existsSync(path.join(REPO_ROOT, rootFile))) found.add(rootFile);
  }

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

function formatInline(raw, currentPage, pageMap, glossaryCtx = null) {
  const protectedTokens = [];
  function stash(htmlFragment) {
    const idx = protectedTokens.length;
    protectedTokens.push(htmlFragment);
    return `\u0000TOK${idx}\u0000`;
  }

  const plainMeasurementRe =
    /^-?\d+(?:\.\d+)?\s*(?:m|cm|mm)?(?:\s*(?:x|×|\/|\*|=|-)\s*-?\d+(?:\.\d+)?\s*(?:m|cm|mm)?)?\s*(?:m|cm|mm|ms|s|W|Wh|kg|Hz|kbps|degrees?|per cent|m\^2)?$/i;

  let text = raw.replace(/`([^`]+)`/g, (_, code) => {
    if (plainMeasurementRe.test(code.trim())) {
      const cleanQty = escapeHtml(code)
        .replace(/\s+x\s+/g, "\u00a0×\u00a0")
        .replace(/m\^2/g, "m²")
        .replace(/\s+(m|cm|mm|ms|s|W|Wh|kg|Hz|kbps|m²)\b/g, "\u00a0$1");
      return stash(cleanQty);
    }
    const formattedCode = escapeHtml(code).replace(/ -&gt; /g, " → ");
    return stash(`<code>${formattedCode}</code>`);
  });

  text = text.replace(/<(https?:\/\/[^>]+)>/g, "[$1]($1)");
  text = escapeHtml(text);
  text = smartTypography(text);

  // Protect links and bold inline definitions before auto-matching glossary terms
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    const resolved = resolveDocHref(href, currentPage, pageMap);
    return stash(`<a href="${resolved}">${label}</a>`);
  });
  text = text.replace(/\*\*([^*]+)\*\*/g, (_, inner) => {
    // If a paragraph explicitly defines a term in bold ("is called **odometry**"), mark that concept as already seen on the page!
    if (glossaryCtx) {
      for (const m of glossaryCtx.matchers) {
        m.regex.lastIndex = 0;
        if (m.regex.test(inner) && inner.trim().length <= m.phrase.length + 6) {
          glossaryCtx.seen.add(m.slug);
        }
      }
    }
    return stash(`<strong>${inner}</strong>`);
  });
  text = text.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  // Auto-match first occurrence per page of glossary terms in plain prose
  if (glossaryCtx && currentPage.repoRel !== "docs/glossary.md") {
    const glossaryHref = relativeHref(currentPage.outRel, "docs/glossary.html");
    for (const m of glossaryCtx.matchers) {
      if (glossaryCtx.seen.has(m.slug)) continue;
      m.regex.lastIndex = 0;
      let matchedOnce = false;
      text = text.replace(m.regex, (match) => {
        if (matchedOnce) return match;
        matchedOnce = true;
        glossaryCtx.seen.add(m.slug);
        return stash(
          `<a class="glossary-term" href="${glossaryHref}#${m.slug}" data-term="${m.slug}">${match}</a>`
        );
      });
    }
  }

  while (/\u0000TOK\d+\u0000/.test(text)) {
    text = text.replace(/\u0000TOK(\d+)\u0000/g, (_, idx) => protectedTokens[Number(idx)]);
  }
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

function renderCodeBlock(content) {
  return `<div class="code-wrap"><button type="button" class="copy-btn" aria-label="Copy code"><svg class="icon-copy" viewBox="0 0 16 16" aria-hidden="true"><rect x="5.5" y="5.5" width="8" height="8" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M10.5 5.5V3.7c0-.7-.5-1.2-1.2-1.2H3.7c-.7 0-1.2.5-1.2 1.2v5.6c0 .7.5 1.2 1.2 1.2h1.8" fill="none" stroke="currentColor" stroke-width="1.5"/></svg><svg class="icon-check" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.2 8.4L6.5 11.7L12.8 4.6" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></button><pre><code>${escapeHtml(
    content
  )}</code></pre></div>`;
}

function parseListBlock(lines, startIdx, ordered, currentPage, pageMap, glossaryCtx) {
  const itemMarkerRe = ordered ? /^\s*\d+\.\s+(.*)$/ : /^\s*-\s+(.*)$/;
  const items = [];
  let i = startIdx;

  while (i < lines.length) {
    const m = lines[i].match(itemMarkerRe);
    if (!m) break;

    const itemParts = [`<p>${formatInline(m[1].trim(), currentPage, pageMap, glossaryCtx)}</p>`];
    i++;

    while (i < lines.length) {
      const cur = lines[i];
      if (!cur.trim()) {
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
        itemParts.push(renderCodeBlock(block.join("\n")));
        continue;
      }

      if (/^\s{2,}-\s+/.test(cur) || /^\s{2,}[a-z]\.\s+/.test(cur)) {
        const subOrdered = /^\s{2,}[a-z]\.\s+/.test(cur);
        const subRe = subOrdered ? /^\s{2,}[a-z]\.\s+(.*)$/ : /^\s{2,}-\s+(.*)$/;
        const subItems = [];
        while (i < lines.length && subRe.test(lines[i])) {
          const sm = lines[i].match(subRe);
          subItems.push(`<li>${formatInline(sm[1].trim(), currentPage, pageMap, glossaryCtx)}</li>`);
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
        itemParts.push(`<p>${formatInline(cont.join(" "), currentPage, pageMap, glossaryCtx)}</p>`);
        continue;
      }

      break;
    }

    if (itemParts.length === 1 && itemParts[0].startsWith("<p>")) {
      items.push(`<li>${itemParts[0].slice(3, -4)}</li>`);
    } else {
      items.push(`<li>${itemParts.join("\n")}</li>`);
    }
  }

  const tag = ordered ? "ol" : "ul";
  return { html: `<${tag}>\n${items.join("\n")}\n</${tag}>`, nextIdx: i };
}

function parseMarkdown(md, currentPage, pageMap, glossaryCatalogue) {
  const cleaned = md.replace(/<!--[\s\S]*?-->/g, "").replace(/\r\n/g, "\n");
  const lines = cleaned.split("\n");
  const htmlParts = [];
  const tocSections = [];
  let currentH2Section = null;
  let currentH3 = "";
  let i = 0;

  const glossaryCtx = glossaryCatalogue
    ? { matchers: glossaryCatalogue.matchers, seen: new Set() }
    : null;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      i++;
      continue;
    }

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
      } else if (
        currentPage.repoRel === "docs/system/navigation-and-mission.md" &&
        content.includes("[XX]")
      ) {
        htmlParts.push(renderCostmapInflationDiagram());
      } else if (
        currentPage.repoRel === "docs/system/teleop-and-control.md" &&
        content.includes("44 52")
      ) {
        htmlParts.push(renderSerialPacketDiagram());
      } else if (
        currentPage.repoRel === "docs/system/teleop-and-control.md" &&
        content.includes("left wheel speed")
      ) {
        htmlParts.push(renderSkidSteerMathBlock());
      } else if (
        currentPage.repoRel === "docs/system/sensors.md" &&
        content.includes("nearest level-ground hit")
      ) {
        htmlParts.push(renderOusterMathBlock());
      } else {
        htmlParts.push(renderCodeBlock(content));
      }
      continue;
    }

    if (line.trim().startsWith("|") && i + 1 < lines.length && /^\s*\|[\s:-]+\|/.test(lines[i + 1])) {
      const headers = parseTableRow(lines[i]);
      i += 2;
      const bodyRows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        bodyRows.push(parseTableRow(lines[i]));
        i++;
      }
      const thead = `<thead><tr>${headers
        .map((h) => `<th>${formatInline(h, currentPage, pageMap, null)}</th>`)
        .join("")}</tr></thead>`;
      const tbody = `<tbody>${bodyRows
        .map(
          (row) =>
            `<tr>${row
              .map((cell) => `<td>${formatInline(cell, currentPage, pageMap, glossaryCtx)}</td>`)
              .join("")}</tr>`
        )
        .join("")}</tbody>`;
      htmlParts.push(`<div class="table-wrap"><table>${thead}${tbody}</table></div>`);
      continue;
    }

    if (line.startsWith(">")) {
      const qLines = [];
      while (i < lines.length && lines[i].startsWith(">")) {
        qLines.push(lines[i].replace(/^>\s?/, ""));
        i++;
      }
      const inner = parseMarkdown(qLines.join("\n"), currentPage, pageMap, null).bodyHtml;
      htmlParts.push(`<blockquote class="math-block">${inner}</blockquote>`);
      continue;
    }

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
      htmlParts.push(
        `<h${depth} id="${id}">${formatInline(rawTitle, currentPage, pageMap, null)}</h${depth}>`
      );
      i++;
      continue;
    }

    if (/^\s*-\s+/.test(line)) {
      const { html, nextIdx } = parseListBlock(lines, i, false, currentPage, pageMap, glossaryCtx);
      htmlParts.push(html);
      i = nextIdx;
      continue;
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      const { html, nextIdx } = parseListBlock(lines, i, true, currentPage, pageMap, glossaryCtx);
      htmlParts.push(html);
      i = nextIdx;
      continue;
    }

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
    htmlParts.push(`<p>${formatInline(paraText, currentPage, pageMap, glossaryCtx)}</p>`);

    function renderPhotoFigure(imgRel, alt, caption, variant = "") {
      const src = relativeHref(currentPage.outRel, imgRel);
      const cls = variant ? ` ${variant}` : "";
      return `<figure class="photo-figure"><div class="photo-frame${cls}"><img src="${src}" alt="${escapeHtml(
        alt
      )}" loading="lazy"/></div><figcaption class="figure-caption">${caption}</figcaption></figure>`;
    }

    if (
      currentPage.repoRel === "docs/system/localisation.md" &&
      currentH3 === "lidar-odometry" &&
      paraText.includes("iterative closest point (ICP)")
    ) {
      htmlParts.push(renderIcpWallDiagram());
    }
    if (
      currentPage.repoRel === "docs/system/localisation.md" &&
      currentH3 === "arena-beacon" &&
      paraText.includes("AprilTag detector")
    ) {
      htmlParts.push(
        renderPhotoFigure(
          "images/apriltag.png",
          "AprilTag 36h11 marker ID 0",
          "Real <code>tag36h11</code> AprilTag (ID 0) from <code>innex_sim</code>. Knowing the physical width of the printed square turns its apparent pixel size and tilt into a 3D pose relative to the camera.",
          "is-tag"
        )
      );
    }
    if (
      currentPage.repoRel === "docs/system/sensors.md" &&
      currentH2Section?.id === "stereo-depth-on-sand" &&
      paraText.includes("active stereo")
    ) {
      htmlParts.push(
        renderPhotoFigure(
          "images/oak-d-pro.png",
          "Luxonis OAK-D Pro active stereo camera",
          "Luxonis OAK-D Pro front face: left and right monochrome stereo lenses on the outer edges, centre colour camera, and the infrared dot projector and flood LED between them. Image: Luxonis.",
          "is-product"
        )
      );
    }
    if (
      currentPage.repoRel === "docs/system/sensors.md" &&
      currentH2Section?.id === "lidar-field-of-view" &&
      paraText.includes("Rev 7")
    ) {
      htmlParts.push(
        renderPhotoFigure(
          "images/ouster-os1.png",
          "Ouster OS1-128 Rev 7 LiDAR sensor",
          "Ouster OS1-128 3D spinning LiDAR sensor. Its 128 vertical laser beams sweep 360 degrees horizontally across a 42.4-degree vertical field of view. Image: Ouster."
        )
      );
    }
    if (
      currentPage.repoRel === "docs/system/sensors.md" &&
      currentH2Section?.id === "lidar-field-of-view" &&
      paraText.includes("0.75 m")
    ) {
      htmlParts.push(renderInteractiveOusterFigure());
    }
    if (
      currentPage.repoRel === "docs/system/perception.md" &&
      !currentH2Section &&
      paraText.includes("moving camera frame")
    ) {
      htmlParts.push(
        renderPhotoFigure(
          "images/point-cloud.jpg",
          "3D LiDAR point cloud captured by an Ouster OS1",
          "Example 3D point cloud captured by an Ouster OS1 LiDAR, coloured by surface reflectivity. Photo: Daniel L. Lu (CC BY 4.0)."
        )
      );
    }
    if (
      currentPage.repoRel === "docs/jetson.md" &&
      !currentH2Section &&
      paraText.includes("JetPack 7.2.1")
    ) {
      htmlParts.push(
        renderPhotoFigure(
          "images/jetson-orin-nano.jpg",
          "NVIDIA Jetson Orin Nano Super Developer Kit",
          "NVIDIA Jetson Orin Nano Super Developer Kit, the rover's main onboard compute module running ROS 2 Jazzy in 25 W mode. Image: NVIDIA."
        )
      );
    }
    if (
      currentPage.repoRel === "firmware/teensy_drive/README.md" &&
      !currentH2Section &&
      paraText.includes("LED_BUILTIN")
    ) {
      htmlParts.push(
        renderPhotoFigure(
          "images/teensy41.jpg",
          "PJRC Teensy 4.1 microcontroller board, top and bottom views",
          "PJRC Teensy 4.1 board (top and bottom views), showing the USB micro-B host port, IMXRT1062 processor and 3.3 V I/O pins. Photo: SpencerWF (CC0)."
        )
      );
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

function writeGlossaryClientScript(entries) {
  const script = `(() => {
  const GLOSSARY = ${JSON.stringify(entries)};
  const triggers = [...document.querySelectorAll("a.glossary-term[data-term]")];
  if (!triggers.length) return;

  const popover = document.createElement("div");
  popover.className = "glossary-popover";
  popover.id = "glossary-popover";
  popover.setAttribute("role", "tooltip");
  popover.setAttribute("aria-hidden", "true");
  document.body.appendChild(popover);

  let activeTrigger = null;
  let openTimer = 0;
  let closeTimer = 0;
  let lastClosedAt = 0;

  const rootPrefix = document.documentElement.dataset.root || ".";
  function resolveAsset(relPath) {
    return rootPrefix === "." ? \`./\${relPath}\` : \`\${rootPrefix}/\${relPath}\`;
  }

  function renderCardContent(entry, glossaryHref) {
    let visualBlock = "";
    if (entry.visual) {
      if (typeof entry.visual === "string") {
        visualBlock = \`<div class="gp-visual">\${entry.visual}</div>\`;
      } else if (entry.visual.type === "img") {
        const cls = entry.visual.fit === "contain" ? " is-contain" : "";
        visualBlock = \`<div class="gp-visual\${cls}"><img src="\${resolveAsset(entry.visual.src)}" alt="\${entry.visual.alt}"/></div>\`;
      }
    }
    const subtitleBlock = entry.subtitle
      ? \`<p class="gp-subtitle">\${entry.subtitle}</p>\`
      : "";
    const extBlock = entry.extUrl
      ? \`<a href="\${entry.extUrl}" target="_blank" rel="noopener noreferrer">\${entry.extLabel} ↗</a>\`
      : "";

    popover.innerHTML = \`
      \${visualBlock}
      <div class="gp-content">
        <p class="gp-title">\${entry.title}</p>
        \${subtitleBlock}
        <p class="gp-body">\${entry.bodyHtml}</p>
      </div>
      <div class="gp-footer">
        <a href="\${glossaryHref}">Glossary entry →</a>
        \${extBlock}
      </div>
    \`;
  }

  function positionCard(trigger) {
    const rect = trigger.getBoundingClientRect();
    const cardW = popover.offsetWidth || 344;
    const cardH = popover.offsetHeight || 220;
    const margin = 16;
    const gap = 9;

    const triggerCenterX = rect.left + rect.width / 2;
    let left = triggerCenterX - cardW / 2;
    left = Math.max(margin, Math.min(window.innerWidth - cardW - margin, left));

    const spaceBelow = window.innerHeight - rect.bottom - margin;
    const placeAbove = spaceBelow < cardH + gap && rect.top > cardH + gap;
    const top = placeAbove ? rect.top - cardH - gap : rect.bottom + gap;

    const originX = Math.max(16, Math.min(cardW - 16, triggerCenterX - left));
    popover.dataset.placement = placeAbove ? "above" : "below";
    popover.style.transformOrigin = \`\${originX.toFixed(0)}px \${placeAbove ? "bottom" : "top"}\`;
    popover.style.left = \`\${left.toFixed(1)}px\`;
    popover.style.top = \`\${top.toFixed(1)}px\`;
  }

  function openFor(trigger) {
    const slug = trigger.dataset.term;
    const entry = GLOSSARY[slug];
    if (!entry) return;

    clearTimeout(closeTimer);
    if (activeTrigger && activeTrigger !== trigger) {
      activeTrigger.removeAttribute("data-open");
      activeTrigger.removeAttribute("aria-describedby");
    }

    activeTrigger = trigger;
    trigger.setAttribute("data-open", "true");
    trigger.setAttribute("aria-describedby", "glossary-popover");
    renderCardContent(entry, trigger.getAttribute("href"));
    popover.setAttribute("aria-hidden", "false");
    positionCard(trigger);
    requestAnimationFrame(() => {
      popover.classList.add("is-visible");
    });
  }

  function closeCard() {
    clearTimeout(openTimer);
    clearTimeout(closeTimer);
    if (!activeTrigger) return;
    activeTrigger.removeAttribute("data-open");
    activeTrigger.removeAttribute("aria-describedby");
    activeTrigger = null;
    lastClosedAt = performance.now();
    popover.classList.remove("is-visible");
    popover.setAttribute("aria-hidden", "true");
  }

  function scheduleClose() {
    clearTimeout(openTimer);
    clearTimeout(closeTimer);
    closeTimer = setTimeout(closeCard, 130);
  }

  for (const trigger of triggers) {
    trigger.addEventListener("pointerenter", (e) => {
      if (e.pointerType === "touch") return;
      clearTimeout(closeTimer);
      clearTimeout(openTimer);
      const warm = activeTrigger !== null || performance.now() - lastClosedAt < 450;
      const delay = warm ? 0 : 260;
      if (delay === 0) {
        openFor(trigger);
      } else {
        openTimer = setTimeout(() => openFor(trigger), delay);
      }
    });

    trigger.addEventListener("pointerleave", (e) => {
      if (e.pointerType === "touch") return;
      scheduleClose();
    });

    // Touch devices: first tap opens preview card; tapping inside card or second tap navigates
    trigger.addEventListener("click", (e) => {
      const coarse = window.matchMedia("(hover: none)").matches;
      if (coarse && activeTrigger !== trigger) {
        e.preventDefault();
        openFor(trigger);
      }
    });

    trigger.addEventListener("focus", () => {
      if (!trigger.matches(":focus-visible")) return;
      clearTimeout(closeTimer);
      clearTimeout(openTimer);
      openTimer = setTimeout(() => openFor(trigger), 180);
    });

    trigger.addEventListener("blur", () => {
      scheduleClose();
    });
  }

  popover.addEventListener("pointerenter", () => {
    clearTimeout(closeTimer);
  });

  popover.addEventListener("pointerleave", () => {
    scheduleClose();
  });

  document.addEventListener("pointerdown", (e) => {
    if (!activeTrigger) return;
    if (!popover.contains(e.target) && !activeTrigger.contains(e.target)) {
      closeCard();
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && activeTrigger) {
      closeCard();
    }
  });

  window.addEventListener(
    "scroll",
    () => {
      if (activeTrigger) positionCard(activeTrigger);
    },
    { passive: true }
  );
  window.addEventListener(
    "resize",
    () => {
      if (activeTrigger) positionCard(activeTrigger);
    },
    { passive: true }
  );
})();
`;
  fs.writeFileSync(path.join(DIST_DIR, "glossary-card.js"), script, "utf8");
}

function buildSearchIndex(flatOrder) {
  const entries = [];
  for (const page of flatOrder) {
    const cleaned = page.md.replace(/<!--[\s\S]*?-->/g, "").replace(/\r\n/g, "\n");
    const chunks = cleaned.split(/^(?=#{1,3}\s+)/m);
    for (const chunk of chunks) {
      const hm = chunk.match(/^(#{1,3})\s+(.+)$/m);
      if (!hm) continue;
      const depth = hm[1].length;
      const secTitle = hm[2].replace(/`([^`]+)`/g, "$1").trim();
      const id = depth === 1 ? "" : slugify(secTitle);
      const bodyText = chunk
        .slice(hm[0].length)
        .replace(/```[\s\S]*?```/g, (b) => b.replace(/```\w*/g, " "))
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
        .replace(/[*`|#>]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
      if (!bodyText && depth === 1) continue;
      entries.push({
        page: page.label,
        sec: depth === 1 ? page.label : secTitle,
        group: page.groupTitle,
        url: id ? `${page.outRel}#${id}` : page.outRel,
        text: bodyText.slice(0, 420),
      });
    }
  }
  return entries;
}

function writeSearchAndCopyScript(searchEntries) {
  const script = `(() => {
  // 1. Copy button on code blocks
  for (const btn of document.querySelectorAll(".copy-btn")) {
    let timer = 0;
    btn.addEventListener("click", async () => {
      const code = btn.parentElement?.querySelector("pre code")?.textContent ?? "";
      try {
        await navigator.clipboard.writeText(code);
        btn.setAttribute("data-copied", "true");
        btn.setAttribute("aria-label", "Copied");
        clearTimeout(timer);
        timer = setTimeout(() => {
          btn.removeAttribute("data-copied");
          btn.setAttribute("aria-label", "Copy code");
        }, 1600);
      } catch {}
    });
  }

  // 2. Instant Cmd+K / "/" documentation search
  const INDEX = ${JSON.stringify(searchEntries)};
  const rootPrefix = document.documentElement.dataset.root || "./";
  const dialog = document.getElementById("search-dialog");
  const input = document.getElementById("search-input");
  const list = document.getElementById("search-results");
  const status = document.getElementById("search-status");
  const openBtn = document.getElementById("search-open");
  const escBtn = document.getElementById("search-esc");
  if (!dialog || !input || !list) return;

  let activeIdx = 0;
  let currentMatches = [];
  let lastTrigger = null;

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function highlight(str, terms) {
    let out = esc(str);
    for (const t of terms) {
      if (t.length < 2) continue;
      const re = new RegExp(\`(\${t.replace(/[.*+?^$\${}()|[\\]\\\\]/g, "\\\\$&")})\`, "ig");
      out = out.replace(re, "<mark>$1</mark>");
    }
    return out;
  }

  function resolveUrl(relUrl) {
    return rootPrefix === "./" ? \`./\${relUrl}\` : \`\${rootPrefix}/\${relUrl}\`;
  }

  function renderResults(query) {
    const q = query.trim().toLowerCase();
    const terms = q ? q.split(/\\s+/).filter(Boolean) : [];

    if (!terms.length) {
      currentMatches = INDEX.slice(0, 10);
    } else {
      const scored = [];
      for (const item of INDEX) {
        const hayTitle = \`\${item.page} \${item.sec}\`.toLowerCase();
        const hayBody = item.text.toLowerCase();
        let score = 0;
        let allMatch = true;
        for (const t of terms) {
          const inT = hayTitle.includes(t);
          const inB = hayBody.includes(t);
          if (!inT && !inB) {
            allMatch = false;
            break;
          }
          if (inT) score += 10;
          if (inB) score += 2;
        }
        if (allMatch) scored.push({ item, score });
      }
      scored.sort((a, b) => b.score - a.score);
      currentMatches = scored.slice(0, 14).map((s) => s.item);
    }

    activeIdx = 0;
    if (!currentMatches.length) {
      list.innerHTML = '<li class="search-empty">No matching sections found.</li>';
      if (status) status.textContent = "0 results";
      return;
    }

    list.innerHTML = currentMatches
      .map((m, idx) => {
        const label = m.page === m.sec ? m.page : \`\${m.page} › \${m.sec}\`;
        let snippet = m.text;
        if (terms.length) {
          const pos = m.text.toLowerCase().indexOf(terms[0]);
          if (pos > 48) snippet = "…" + m.text.slice(pos - 28);
        }
        return \`<li class="search-item" id="sr-\${idx}" role="option" aria-selected="\${idx === 0 ? "true" : "false"}">
          <a href="\${resolveUrl(m.url)}">
            <span class="search-item-top">
              <span class="search-item-title">\${highlight(label, terms)}</span>
              <span class="search-item-group">\${esc(m.group)}</span>
            </span>
            <span class="search-item-snippet">\${highlight(snippet.slice(0, 140), terms)}</span>
          </a>
        </li>\`;
      })
      .join("");
    input.setAttribute("aria-activedescendant", "sr-0");
    if (status) status.textContent = \`\${currentMatches.length} results\`;
  }

  function setSelection(nextIdx) {
    const items = [...list.querySelectorAll(".search-item")];
    if (!items.length) return;
    activeIdx = (nextIdx + items.length) % items.length;
    items.forEach((el, idx) => {
      el.setAttribute("aria-selected", idx === activeIdx ? "true" : "false");
    });
    input.setAttribute("aria-activedescendant", \`sr-\${activeIdx}\`);
    items[activeIdx].scrollIntoView({ block: "nearest" });
  }

  function openSearch() {
    if (dialog.open) return;
    lastTrigger = document.activeElement;
    dialog.showModal();
    renderResults(input.value);
    input.focus();
    input.select();
  }

  function closeSearch() {
    if (!dialog.open) return;
    dialog.close();
    if (lastTrigger && typeof lastTrigger.focus === "function") {
      lastTrigger.focus();
    }
  }

  openBtn?.addEventListener("click", openSearch);
  escBtn?.addEventListener("click", closeSearch);
  input.addEventListener("input", () => renderResults(input.value));

  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelection(activeIdx + 1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelection(activeIdx - 1);
    } else if (e.key === "Enter") {
      const link = list.querySelectorAll(".search-item a")[activeIdx];
      if (link) {
        e.preventDefault();
        const href = link.getAttribute("href");
        closeSearch();
        window.location.href = href;
      }
    }
  });

  list.addEventListener("click", (e) => {
    if (e.target.closest("a")) closeSearch();
  });

  dialog.addEventListener("click", (e) => {
    if (e.target === dialog) closeSearch();
  });

  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      dialog.open ? closeSearch() : openSearch();
      return;
    }
    if (
      e.key === "/" &&
      !dialog.open &&
      !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName || "") &&
      !document.activeElement?.isContentEditable
    ) {
      e.preventDefault();
      openSearch();
    }
  });
})();
`;
  fs.writeFileSync(path.join(DIST_DIR, "search-ui.js"), script, "utf8");
}

function copyStaticAssets() {
  fs.mkdirSync(DIST_DIR, { recursive: true });
  fs.writeFileSync(path.join(DIST_DIR, ".nojekyll"), "", "utf8");
  fs.copyFileSync(path.join(__dirname, "styles.css"), path.join(DIST_DIR, "styles.css"));
  const distFonts = path.join(DIST_DIR, "fonts");
  fs.mkdirSync(distFonts, { recursive: true });
  if (fs.existsSync(FONTS_DIR)) {
    for (const f of fs.readdirSync(FONTS_DIR)) {
      fs.copyFileSync(path.join(FONTS_DIR, f), path.join(distFonts, f));
    }
  }
  const distImages = path.join(DIST_DIR, "images");
  fs.mkdirSync(distImages, { recursive: true });
  if (fs.existsSync(IMAGES_DIR)) {
    for (const f of fs.readdirSync(IMAGES_DIR)) {
      fs.copyFileSync(path.join(IMAGES_DIR, f), path.join(distImages, f));
    }
  }
}

function buildAllPages() {
  copyStaticAssets();
  const glossaryCatalogue = parseGlossaryCatalogue();
  writeGlossaryClientScript(glossaryCatalogue.entries);
  const { groups, pageMap, flatOrder } = discoverDocs();
  writeSearchAndCopyScript(buildSearchIndex(flatOrder));

  flatOrder.forEach((page, idx) => {
    const { bodyHtml, tocSections } = parseMarkdown(page.md, page, pageMap, glossaryCatalogue);
    const sidebarHtml = renderSidebar(groups, page);
    const tocHtml = renderToc(tocSections, page.label);

    const outDir = path.posix.dirname(page.outRel);
    const rootPrefix = outDir === "." ? "." : path.posix.relative(outDir, "");
    const cssHref = relativeHref(page.outRel, "styles.css");
    const glossaryScriptHref = relativeHref(page.outRel, "glossary-card.js");
    const searchScriptHref = relativeHref(page.outRel, "search-ui.js");
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
<html lang="en-GB" data-root="${rootPrefix}">
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
      <button type="button" class="search-trigger" id="search-open" aria-label="Search documentation (Command K)">
        <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="6.8" cy="6.8" r="4.8" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="10.4" y1="10.4" x2="14" y2="14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        <span>Search</span>
        <kbd class="search-kbd">⌘K</kbd>
      </button>
      <a class="topbar-link" href="${rulesHref}">Rules</a>
      <a class="topbar-link" href="${glossaryHref}">Glossary</a>
      <a class="topbar-link" href="https://github.com/InnovaRobotics/innex-1">GitHub</a>
    </nav>
  </header>

  <dialog class="search-dialog" id="search-dialog" aria-label="Search documentation">
    <div class="search-header">
      <svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="6.8" cy="6.8" r="4.8" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="10.4" y1="10.4" x2="14" y2="14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      <label for="search-input" class="sr-only">Search documentation</label>
      <input id="search-input" class="search-input" type="search" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="true" aria-controls="search-results" placeholder="Search pages, ROS topics, commands…"/>
      <button type="button" class="search-esc" id="search-esc" aria-label="Close search">Esc</button>
    </div>
    <div id="search-status" class="sr-only" role="status"></div>
    <ul class="search-results" id="search-results" role="listbox" aria-label="Search results"></ul>
  </dialog>

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

  <script src="${glossaryScriptHref}" defer></script>
  <script src="${searchScriptHref}" defer></script>
  <script>
    (() => {
      const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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

      const sliderOuster = document.getElementById("slider-ouster-h");
      if (sliderOuster) {
        const tan212 = Math.tan((21.2 * Math.PI) / 180);
        const sensorBodyH = 0.0583;
        const groundY = 186;
        const pxPerMVert = 130;
        const originX = 96;
        const pxPerMHoriz = 175;

        const riserEl = document.getElementById("ouster-riser");
        const bodyEl = document.getElementById("ouster-body");
        const fanEl = document.getElementById("ouster-fan");
        const topRayEl = document.getElementById("ouster-top-ray");
        const botRayEl = document.getElementById("ouster-bot-ray");
        const hitDotEl = document.getElementById("ouster-hit-dot");
        const hitLabelEl = document.getElementById("ouster-hit-label");

        const labelH = document.getElementById("label-ouster-h");
        const outBase = document.getElementById("ouster-out-base");
        const outTop = document.getElementById("ouster-out-top");
        const outHit = document.getElementById("ouster-out-hit");
        const outBox = document.getElementById("ouster-out-box");
        const oPresets = [...document.querySelectorAll(".ouster-preset")];
        const oInd = document.getElementById("ouster-preset-indicator");

        let curH = 0.94;
        let oRaf = 0;
        const easeO = (t) => 1 - Math.pow(1 - t, 3.6);

        function syncOusterInd() {
          if (!oInd) return;
          const active = oPresets.find((b) => b.getAttribute("aria-pressed") === "true");
          if (!active) {
            oInd.style.opacity = "0";
            return;
          }
          oInd.style.opacity = "1";
          oInd.style.width = \`\${active.offsetWidth}px\`;
          oInd.style.transform = \`translateX(\${active.offsetLeft}px)\`;
        }

        function renderOuster(h) {
          curH = h;
          const topH = h + sensorBodyH;
          const hitM = h / tan212;
          const baseY = groundY - h * pxPerMVert;
          const opticY = baseY - 4;
          const hitX = Math.min(668, originX + hitM * pxPerMHoriz);

          riserEl.setAttribute("y2", baseY.toFixed(1));
          bodyEl.setAttribute("y", (baseY - 8).toFixed(1));
          const topEndY = Math.max(8, opticY - 48);
          fanEl.setAttribute("points", \`\${originX},\${opticY.toFixed(1)} 676,\${topEndY.toFixed(1)} 676,\${groundY} \${hitX.toFixed(1)},\${groundY}\`);
          topRayEl.setAttribute("y1", opticY.toFixed(1));
          topRayEl.setAttribute("y2", topEndY.toFixed(1));
          botRayEl.setAttribute("y1", opticY.toFixed(1));
          botRayEl.setAttribute("x2", hitX.toFixed(1));
          hitDotEl.setAttribute("cx", hitX.toFixed(1));
          hitLabelEl.setAttribute("x", Math.min(622, hitX).toFixed(1));
          hitLabelEl.textContent = \`\${hitM.toFixed(2)} m first hit\`;

          labelH.textContent = \`\${h.toFixed(2)} m\`;
          outBase.textContent = \`\${h.toFixed(2)} m\`;
          outTop.textContent = \`\${topH.toFixed(2)} m\`;
          outHit.textContent = \`\${hitM.toFixed(2)} m\`;
          outBox.textContent = topH <= 0.75 ? "Fits inside 0.75 m" : "Fold for inspection";
          outBox.classList.toggle("is-accent", topH <= 0.75);
        }

        function markOusterPreset(h) {
          for (const b of oPresets) {
            b.setAttribute("aria-pressed", Math.abs(Number(b.dataset.h) - h) < 0.005 ? "true" : "false");
          }
          syncOusterInd();
        }

        function animateOuster(targetH) {
          cancelAnimationFrame(oRaf);
          markOusterPreset(targetH);
          if (reducedMotion()) {
            sliderOuster.value = targetH.toFixed(2);
            renderOuster(targetH);
            return;
          }
          const startH = curH;
          const t0 = performance.now();
          const dur = 280;
          function step(now) {
            const p = Math.min(1, (now - t0) / dur);
            const val = startH + (targetH - startH) * easeO(p);
            sliderOuster.value = val.toFixed(2);
            renderOuster(val);
            if (p < 1) oRaf = requestAnimationFrame(step);
          }
          oRaf = requestAnimationFrame(step);
        }

        sliderOuster.addEventListener("input", () => {
          cancelAnimationFrame(oRaf);
          const v = Number(sliderOuster.value);
          markOusterPreset(v);
          renderOuster(v);
        });
        for (const b of oPresets) {
          b.addEventListener("click", () => animateOuster(Number(b.dataset.h)));
        }
        renderOuster(0.94);
        requestAnimationFrame(syncOusterInd);
        document.fonts?.ready?.then(syncOusterInd);
        window.addEventListener("resize", syncOusterInd, { passive: true });
      }

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
      document.fonts?.ready?.then(syncPresetIndicator);
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
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
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
