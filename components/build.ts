import { build, type InlineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import fg from "fast-glob";
import path from "path";
import fs from "fs";
import crypto from "crypto";

const entries = fg.sync("src/**/index.tsx");
const outDir = "assets";

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
function generateFileHash(filePath: string, length: number = 4): string {
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

  // Generate content-based hashes
  const jsPath = path.join(outDir, `${name}.js`);
  const cssPath = path.join(outDir, `${name}.css`);

  if (!fs.existsSync(jsPath)) {
    throw new Error(`Build failed: ${jsPath} not found`);
  }

  const jsHash = generateFileHash(jsPath);
  const cssHash = fs.existsSync(cssPath) ? generateFileHash(cssPath) : "";

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

  console.log(`✓ Built ${name}`);

  return {
    name,
    jsHash,
    cssHash,
    jsPath: hashedJsPath,
    cssPath: hashedCssPath,
  };
}

/**
 * Generate HTML file for a widget.
 */
function generateHtml(artifact: BuildArtifact, baseUrl: string): string {
  const { name, jsHash, cssHash } = artifact;

  const scriptUrl = `${baseUrl}/${name}-${jsHash}.js`;
  const cssUrl = cssHash ? `${baseUrl}/${name}-${cssHash}.css` : "";

  const cssLink = cssUrl
    ? `  <link rel="stylesheet" href="${cssUrl}">\n`
    : "";

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
  console.log("Building widgets with content-based hashing...\n");

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

    // Write live HTML (used by MCP server)
    const liveHtmlPath = path.join(outDir, `${artifact.name}.html`);
    fs.writeFileSync(liveHtmlPath, html, { encoding: "utf8" });
    console.log(`  Generated ${artifact.name}.html`);
  }

  console.log("\n✓ Build complete!");
  console.log("\nArtifacts:");
  for (const artifact of artifacts) {
    console.log(`  ${artifact.name}:`);
    console.log(`    JS:  ${path.basename(artifact.jsPath)} (hash: ${artifact.jsHash})`);
    if (artifact.cssHash) {
      console.log(`    CSS: ${path.basename(artifact.cssPath)} (hash: ${artifact.cssHash})`);
    }
  }
}

main().catch((err) => {
  console.error("Build failed:", err);
  process.exit(1);
});
