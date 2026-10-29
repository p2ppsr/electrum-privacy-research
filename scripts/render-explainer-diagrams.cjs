// Render local Mermaid sources to portable, accessible SVGs; no research data fetched.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { chromium } = require(process.argv[2] || 'playwright');

const root = path.resolve(__dirname, '..');
const cases = [
  ['explainer-shop', 'How one checkout address identifies a wider shop profile',
    'The wallet sends fingerprints together. One matching checkout address labels the saved group as shop-associated. Other matching payments can then be linked.'],
  ['explainer-lasting-watch', 'The old operator can keep watching after the wallet leaves',
    'The earlier fingerprint list and later public blockchain records let the old operator recognize matching receipts and spends without a new wallet connection.'],
  ['explainer-payment-links', 'Controlled payment example with fictional amounts and no real money',
    'Observed wallets A and B pay 2.5 million and 4 million test sats to a shop profile. An unidentified payer sends 1.25 million. The shop sends 1.1 million to an unidentified recipient.'],
];
const digest = data => crypto.createHash('sha256').update(data).digest('hex');

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 784, height: 1200 }, ignoreHTTPSErrors: true });
    await page.setContent('<html><body style="margin:24px;background:white"><main id="diagram"></main></body></html>');
    await page.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.min.js' });
    await page.evaluate(() => mermaid.initialize({
      startOnLoad: false, theme: 'base', htmlLabels: false, deterministicIds: true,
      deterministicIDSeed: 'electrum-privacy-explainer',
      themeVariables: { primaryColor: '#f4f4f4', primaryTextColor: '#111111', primaryBorderColor: '#666666',
        lineColor: '#555555', edgeLabelBackground: '#ffffff', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: '18px' },
      flowchart: { htmlLabels: false, useMaxWidth: true, wrappingWidth: 210, nodeSpacing: 35, rankSpacing: 48 },
    }));
    const previews = path.join(root, '.runtime', 'explainer-diagram-qa');
    fs.mkdirSync(previews, { recursive: true });
    const rows = [];
    for (const [name, title, description] of cases) {
      const sourcePath = path.join(root, 'diagrams', name + '.mmd');
      const source = fs.readFileSync(sourcePath, 'utf8');
      const { svg } = await page.evaluate(async ({ name, source }) => mermaid.render(name, source), { name, source });
      await page.locator('#diagram').evaluate((el, markup) => { el.innerHTML = markup; }, svg);
      const exported = await page.locator('svg').evaluate((svg, { name, title, description }) => {
        const ns = 'http://www.w3.org/2000/svg';
        svg.style.backgroundColor = '#ffffff';
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-labelledby', name + '-title ' + name + '-description');
        const heading = document.createElementNS(ns, 'title');
        heading.id = name + '-title'; heading.textContent = title;
        const desc = document.createElementNS(ns, 'desc');
        desc.id = name + '-description'; desc.textContent = description;
        svg.prepend(heading, desc);
        return svg.outerHTML;
      }, { name, title, description });
      fs.writeFileSync(path.join(root, 'diagrams', name + '.svg'), exported + '\n');
      await page.locator('#diagram').screenshot({ path: path.join(previews, name + '.png') });
      const at736 = await page.locator('svg').boundingBox();
      await page.setViewportSize({ width: 438, height: 1400 });
      await page.locator('#diagram').screenshot({ path: path.join(previews, name + '-narrow.png') });
      const at390 = await page.locator('svg').boundingBox();
      await page.setViewportSize({ width: 784, height: 1200 });
      if (at736.width > 737 || at390.width > 391) throw new Error('Diagram overflow: ' + name);
      if (exported.includes('<foreignObject')) throw new Error('Nonportable HTML label: ' + name);
      rows.push({ name, mermaid_version: '11.12.0', parse_and_render: 'PASS',
        source_sha256: digest(source), svg_sha256: digest(exported + '\n'),
        width_736_view: at736, width_390_view: at390, html_labels: false,
        accessible_svg_title_and_description: true });
    }
    const out = path.join(root, 'evidence', 'explainer-20261028');
    fs.mkdirSync(out, { recursive: true });
    fs.writeFileSync(path.join(out, 'diagram-validation.json'), JSON.stringify(rows, null, 2) + '\n');
    process.stdout.write(JSON.stringify(rows, null, 2) + '\n');
  } finally {
    await browser.close();
  }
})().catch(error => { process.stderr.write(String(error) + '\n'); process.exitCode = 1; });
