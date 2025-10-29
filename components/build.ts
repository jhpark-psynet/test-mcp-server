import { build, type InlineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import fg from "fast-glob";
import path from "path";
import fs from "fs";
import crypto from "crypto";
import pkg from "./package.json" with { type: "json" };

const entries = fg.sync("src/**/index.tsx");
const outDir = "assets";

fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

const builtNames: string[] = [];

for (const file of entries) {
  const name = path.basename(path.dirname(file));
  const entryAbs = path.resolve(file);

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

  console.log(`Building ${name}...`);
  await build(createConfig());
  builtNames.push(name);
  console.log(`Built ${name}`);
}

// Hash outputs for cache busting
const outputs = fs
  .readdirSync(outDir)
  .filter((f) => f.endsWith(".js") || f.endsWith(".css"))
  .map((f) => path.join(outDir, f))
  .filter((p) => fs.existsSync(p));

const h = crypto
  .createHash("sha256")
  .update(pkg.version, "utf8")
  .digest("hex")
  .slice(0, 4);

console.log("Hashing outputs...");
for (const out of outputs) {
  const dir = path.dirname(out);
  const ext = path.extname(out);
  const base = path.basename(out, ext);
  const newName = path.join(dir, `${base}-${h}${ext}`);

  fs.renameSync(out, newName);
  console.log(`${out} -> ${newName}`);
}

// Generate HTML files
const defaultBaseUrl = "http://localhost:4444";
const baseUrlCandidate = process.env.BASE_URL?.trim() ?? "";
const baseUrlRaw = baseUrlCandidate.length > 0 ? baseUrlCandidate : defaultBaseUrl;
const normalizedBaseUrl = baseUrlRaw.replace(/\/+$/, "") || defaultBaseUrl;
console.log(`Using BASE_URL ${normalizedBaseUrl} for generated HTML`);

for (const name of builtNames) {
  const hashedHtmlPath = path.join(outDir, `${name}-${h}.html`);
  const liveHtmlPath = path.join(outDir, `${name}.html`);
  const html = `<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script type="module" src="${normalizedBaseUrl}/${name}-${h}.js"></script>
  <link rel="stylesheet" href="${normalizedBaseUrl}/${name}-${h}.css">
</head>
<body>
  <div id="${name}-root"></div>
</body>
</html>
`;
  fs.writeFileSync(hashedHtmlPath, html, { encoding: "utf8" });
  fs.writeFileSync(liveHtmlPath, html, { encoding: "utf8" });
  console.log(`Generated ${liveHtmlPath}`);
}

console.log("\nBuild complete!");
