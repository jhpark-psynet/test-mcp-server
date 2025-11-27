import fs from 'fs';
import path from 'path';
import fg from 'fast-glob';

const ASSETS_DIR = 'assets';
const REQUIRED_WIDGETS = ['example'];

interface VerificationResult {
  widget: string;
  html: boolean;
  js: string[];
  css: string[];
  htmlReferences: {
    jsRef: string;
    cssRef: string;
    jsExists: boolean;
    cssExists: boolean;
  } | null;
}

/**
 * Extract asset references from HTML.
 */
function extractHtmlReferences(htmlContent: string): { js: string; css: string } | null {
  const scriptMatch = htmlContent.match(/<script[^>]+src="[^"]*\/([^"]+\.js)"/);
  const cssMatch = htmlContent.match(/<link[^>]+href="[^"]*\/([^"]+\.css)"/);

  if (!scriptMatch) {
    return null;
  }

  return {
    js: scriptMatch[1],
    css: cssMatch ? cssMatch[1] : '',
  };
}

/**
 * Verify a single widget.
 */
function verifyWidget(widget: string): VerificationResult {
  const htmlPath = path.join(ASSETS_DIR, `${widget}.html`);
  const htmlExists = fs.existsSync(htmlPath);

  // Find JS/CSS files (with or without hash)
  const jsFiles = fg.sync([
    `${ASSETS_DIR}/${widget}-*.js`,
    `${ASSETS_DIR}/${widget}.js`,
  ]);
  const cssFiles = fg.sync([
    `${ASSETS_DIR}/${widget}-*.css`,
    `${ASSETS_DIR}/${widget}.css`,
  ]);

  let htmlReferences = null;

  if (htmlExists) {
    const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
    const refs = extractHtmlReferences(htmlContent);

    if (refs) {
      htmlReferences = {
        jsRef: refs.js,
        cssRef: refs.css,
        jsExists: fs.existsSync(path.join(ASSETS_DIR, refs.js)),
        cssExists: refs.css ? fs.existsSync(path.join(ASSETS_DIR, refs.css)) : true,
      };
    }
  }

  return {
    widget,
    html: htmlExists,
    js: jsFiles.map(f => path.basename(f)),
    css: cssFiles.map(f => path.basename(f)),
    htmlReferences,
  };
}

/**
 * Print verification result.
 */
function printResult(result: VerificationResult): boolean {
  console.log(`Widget: ${result.widget}`);

  let hasError = false;

  // Check HTML
  if (result.html) {
    console.log(`  HTML: ✅ ${result.widget}.html`);
  } else {
    console.log(`  HTML: ❌ ${result.widget}.html (NOT FOUND)`);
    hasError = true;
  }

  // Check JS
  if (result.js.length > 0) {
    console.log(`  JS:   ✅ ${result.js.join(', ')}`);
  } else {
    console.log(`  JS:   ❌ No JS files found`);
    hasError = true;
  }

  // Check CSS
  if (result.css.length > 0) {
    console.log(`  CSS:  ✅ ${result.css.join(', ')}`);
  } else {
    console.log(`  CSS:  ⚠️  No CSS files found (may be intentional)`);
  }

  // Check HTML references
  if (result.htmlReferences) {
    const { jsRef, cssRef, jsExists, cssExists } = result.htmlReferences;

    if (jsExists) {
      console.log(`  HTML → JS:  ✅ ${jsRef}`);
    } else {
      console.log(`  HTML → JS:  ❌ ${jsRef} (REFERENCED BUT NOT FOUND)`);
      hasError = true;
    }

    if (cssRef) {
      if (cssExists) {
        console.log(`  HTML → CSS: ✅ ${cssRef}`);
      } else {
        console.log(`  HTML → CSS: ❌ ${cssRef} (REFERENCED BUT NOT FOUND)`);
        hasError = true;
      }
    }
  } else if (result.html) {
    console.log(`  HTML references: ❌ Could not parse HTML references`);
    hasError = true;
  }

  console.log();
  return hasError;
}

/**
 * Main verification process.
 */
function main() {
  console.log('Verifying widget builds...\n');
  console.log('='.repeat(60));

  if (!fs.existsSync(ASSETS_DIR)) {
    console.error(`❌ Assets directory not found: ${ASSETS_DIR}`);
    console.error('\nRun "npm run build" first.');
    process.exit(1);
  }

  let hasError = false;
  const results: VerificationResult[] = [];

  // Verify each widget
  for (const widget of REQUIRED_WIDGETS) {
    const result = verifyWidget(widget);
    results.push(result);

    const widgetHasError = printResult(result);
    if (widgetHasError) {
      hasError = true;
    }
  }

  // Summary
  console.log('='.repeat(60));

  if (hasError) {
    console.error('❌ Build verification FAILED!');
    console.error('\nIssues found:');

    for (const result of results) {
      const issues: string[] = [];

      if (!result.html) {
        issues.push('Missing HTML');
      }
      if (result.js.length === 0) {
        issues.push('Missing JS');
      }
      if (result.htmlReferences && !result.htmlReferences.jsExists) {
        issues.push('Broken JS reference');
      }
      if (result.htmlReferences && result.htmlReferences.cssRef && !result.htmlReferences.cssExists) {
        issues.push('Broken CSS reference');
      }

      if (issues.length > 0) {
        console.error(`  ${result.widget}: ${issues.join(', ')}`);
      }
    }

    console.error('\nPlease fix the build and try again.');
    process.exit(1);
  }

  console.log('✅ All widget builds verified successfully!');
  console.log(`\nVerified ${results.length} widget(s):`);
  for (const result of results) {
    console.log(`  - ${result.widget}`);
  }
  console.log();
}

main();
