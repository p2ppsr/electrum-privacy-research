# Explainer diagrams

`EXPLAINER.md` displays the SVG exports so readers do not need a diagram renderer. Each image has descriptive alternative text, an SVG title/description and a nearby prose explanation. The `.mmd` files are the editable Mermaid sources.

The renderer uses Mermaid **11.12.0**, plain SVG text labels and a white background for readable exported images. It loads that pinned renderer from jsDelivr; it does not upload the research, query a wallet or contact a wallet service. It requires Node.js, Playwright and its Chromium runtime:

```bash
node scripts/render-explainer-diagrams.cjs
```

If Playwright is supplied elsewhere, pass its module path as the first argument. Rendering writes SVGs under `diagrams/`, a receipt under `evidence/explainer-20261028/`, and ignored QA previews under `.runtime/explainer-diagram-qa/`. Inspect the previews before removing that disposable directory.

The payment figure uses manufactured test amounts with no monetary value. It illustrates the retained [controlled reconstruction](../evidence/correlation-attempt-01/correlation.json), not actual shop or customer records.
