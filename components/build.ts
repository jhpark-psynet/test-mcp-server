import { build, type InlineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import fg from "fast-glob";
import path from "path";
import fs from "fs";
import crypto from "crypto";

const entries = fg.sync("src/**/index.tsx");
const outDir = "assets";

// Check if hashing should be used (default: false for simplicity)
const USE_HASH = process.env.USE_HASH === "true";

// Clean output directory
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

interface BuildArtifact {
  name: string;
  jsHash: string;
  cssHash: string;
  jsPath: string;
  cssPath: string;
}

const artifacts: BuildArtifact[] = [];

/**
 * Generate content-based hash for a file.
 */
function generateFileHash(filePath: string, length: number = 8): string {
  const content = fs.readFileSync(filePath);
  return crypto
    .createHash("sha256")
    .update(content)
    .digest("hex")
    .slice(0, length);
}

/**
 * Build a single widget component.
 */
async function buildWidget(file: string): Promise<BuildArtifact> {
  const name = path.basename(path.dirname(file));
  const entryAbs = path.resolve(file);

  console.log(`Building ${name}...`);

  const createConfig = (): InlineConfig => ({
    plugins: [tailwindcss(), react()],
    esbuild: {
      jsx: "automatic",
      jsxImportSource: "react",
      target: "es2022",
    },
    build: {
      target: "es2022",
      outDir,
      emptyOutDir: false,
      minify: "esbuild",
      cssCodeSplit: false,
      rollupOptions: {
        input: entryAbs,
        output: {
          format: "es",
          entryFileNames: `${name}.js`,
          inlineDynamicImports: true,
          assetFileNames: (info) =>
            (info.name || "").endsWith(".css")
              ? `${name}.css`
              : `[name]-[hash][extname]`,
        },
        preserveEntrySignatures: "allow-extension",
        treeshake: true,
      },
    },
  });

  await build(createConfig());

  const jsPath = path.join(outDir, `${name}.js`);
  const cssPath = path.join(outDir, `${name}.css`);

  if (!fs.existsSync(jsPath)) {
    throw new Error(`Build failed: ${jsPath} not found`);
  }

  let jsHash = "";
  let cssHash = "";
  let finalJsPath = jsPath;
  let finalCssPath = fs.existsSync(cssPath) ? cssPath : "";

  if (USE_HASH) {
    // Generate content-based hashes
    jsHash = generateFileHash(jsPath);
    cssHash = fs.existsSync(cssPath) ? generateFileHash(cssPath) : "";

    // Rename files with content hashes
    const hashedJsPath = path.join(outDir, `${name}-${jsHash}.js`);
    const hashedCssPath = cssHash
      ? path.join(outDir, `${name}-${cssHash}.css`)
      : "";

    fs.renameSync(jsPath, hashedJsPath);
    console.log(`  JS:  ${path.basename(jsPath)} -> ${path.basename(hashedJsPath)}`);

    if (hashedCssPath && fs.existsSync(cssPath)) {
      fs.renameSync(cssPath, hashedCssPath);
      console.log(`  CSS: ${path.basename(cssPath)} -> ${path.basename(hashedCssPath)}`);
    }

    finalJsPath = hashedJsPath;
    finalCssPath = hashedCssPath;
  } else {
    // No hashing - use simple names
    console.log(`  JS:  ${path.basename(jsPath)}`);
    if (fs.existsSync(cssPath)) {
      console.log(`  CSS: ${path.basename(cssPath)}`);
    }
  }

  console.log(`✓ Built ${name}`);

  return {
    name,
    jsHash,
    cssHash,
    jsPath: finalJsPath,
    cssPath: finalCssPath,
  };
}

/**
 * Generate HTML file for a widget.
 */
function generateHtml(artifact: BuildArtifact, baseUrl: string): string {
  const { name, jsHash, cssHash } = artifact;

  const scriptUrl = USE_HASH && jsHash
    ? `${baseUrl}/${name}-${jsHash}.js`
    : `${baseUrl}/${name}.js`;

  const cssUrl = USE_HASH && cssHash
    ? `${baseUrl}/${name}-${cssHash}.css`
    : `${baseUrl}/${name}.css`;

  const cssLink = `  <link rel="stylesheet" href="${cssUrl}">\n`;

  return `<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script type="module" src="${scriptUrl}"></script>
${cssLink}</head>
<body>
  <div id="${name}-root"></div>
</body>
</html>
`;
}

/**
 * Main build process.
 */
async function main() {
  console.log("Building widgets...\n");

  // Build all widgets
  for (const file of entries) {
    const artifact = await buildWidget(file);
    artifacts.push(artifact);
  }

  // Get base URL
  const defaultBaseUrl = "http://localhost:4444";
  const baseUrlCandidate = process.env.BASE_URL?.trim() ?? "";
  const baseUrlRaw = baseUrlCandidate.length > 0 ? baseUrlCandidate : defaultBaseUrl;
  const normalizedBaseUrl = baseUrlRaw.replace(/\/+$/, "") || defaultBaseUrl;

  console.log(`\nUsing BASE_URL: ${normalizedBaseUrl}`);
  console.log("\nGenerating HTML files...");

  // Generate HTML files
  for (const artifact of artifacts) {
    const html = generateHtml(artifact, normalizedBaseUrl);

    // Write HTML files
    const liveHtmlPath = path.join(outDir, `${artifact.name}.html`);
    fs.writeFileSync(liveHtmlPath, html, { encoding: "utf8" });

    if (USE_HASH && artifact.jsHash) {
      // Also write hashed HTML for CDN deployment
      const hashedHtmlPath = path.join(outDir, `${artifact.name}-${artifact.jsHash}.html`);
      fs.writeFileSync(hashedHtmlPath, html, { encoding: "utf8" });
    }

    console.log(`  ✓ ${artifact.name}.html`);
  }

  // Generate manifest.json
  const manifest: Record<string, string> = {};
  for (const artifact of artifacts) {
    manifest[artifact.name] = USE_HASH && artifact.jsHash ? artifact.jsHash : artifact.name;
  }

  const manifestPath = path.join(outDir, "manifest.json");
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), { encoding: "utf8" });
  console.log(`  ✓ manifest.json`);

  console.log(`\nHash mode: ${USE_HASH ? "enabled" : "disabled"}`);

  // Print summary
  console.log("\n" + "=".repeat(60));
  console.log("Build Summary");
  console.log("=".repeat(60));
  console.log(`Widgets built: ${artifacts.length}`);
  console.log(`Output directory: ${outDir}/`);
  console.log("\nArtifacts:");
  for (const artifact of artifacts) {
    console.log(`  ${artifact.name}:`);
    console.log(`    JS:  ${path.basename(artifact.jsPath)}`);
    if (artifact.cssPath) {
      console.log(`    CSS: ${path.basename(artifact.cssPath)}`);
    }
    console.log(`    HTML: ${artifact.name}.html`);
  }
  console.log("=".repeat(60));
  console.log("\n✅ Build complete!\n");
}

main().catch((err) => {
  console.error("Build failed:", err);
  process.exit(1);
});
