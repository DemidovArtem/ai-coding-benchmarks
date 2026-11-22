# Visual assets and provenance

Prepared **22 November 2026**. All assets are local; presenting needs no network.

## Actual screenshots and upstream artwork

| Local file | Provenance | Use and attribution |
| --- | --- | --- |
| `codex-plan-ui.png` | [I1: Codecademy, Codex app for macOS](https://www.codecademy.com/article/open-ai-codex-app-for-mac-os); [original image](https://static-assets.codecademy.com/february-articles/openai-codex-app-for-macos/chat-commands.png) | Earlier desktop UI, contextual screenshot excerpt. Credit: Codecademy. Current `/plan` behaviour checked against OpenAI docs. |
| `claude-plan-ui.png` | [I2: Paweł Huryn / Product Compass](https://www.productcompass.pm/p/claude-opus-4-7-guide); [original image](https://substack-post-media.s3.amazonaws.com/public/images/f32f7ec3-b1fa-4512-9843-a02434dc61eb_1405x936.png) | Claude Code in VS Code, contextual screenshot excerpt. Credit: Paweł Huryn / Product Compass. Not a current desktop screenshot. |
| `openai-plan-doc.png` | [OpenAI Codex best practices](https://learn.chatgpt.com/guides/best-practices) | Actual browser capture, cropped to “Plan first for difficult tasks.” |
| `claude-plan-doc.png` | [Anthropic common workflows](https://code.claude.com/docs/en/common-workflows#plan-before-editing) | Actual browser capture, cropped to “Plan before editing.” |
| `anthropic-check-doc.png` | [Anthropic best practices](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run) | Actual browser capture, cropped to “Give Claude a check to run.” |
| `ponytail-logo.png` | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), `assets/logo.png` | Upstream project illustration. Copyright Dietrich Gebert; MIT license retained in `PONYTAIL-LICENSE.txt`. |

Menu images retain their source pixels. CSS crops the relevant control and overlays a red rectangle; documentation captures have red underlines overlaid. Source text and interface labels are not rewritten. Client/version scope is visible on the slide and explained in the notes. External screenshots are credited excerpts, not licensed as original work of this project.

## Generated illustrations

Generated with the **built-in image_gen tool**, not a CLI/API fallback. The selected PNGs were copied into this directory after visual inspection. They contain no employer data and are marked illustrative in the deck. They are not proof of a real agent response, browser test or measured outcome. Reuse across adjacent frames is intentional for progressive reveals.

### `complexity-house.png`

Prompt:

> Use case: illustration-story. Asset: wide 16:9 illustration for an English product-management talk called Beyond Vibe Coding. Create a tasteful editorial illustration, very high quality, sparse warm ivory background #f8f7f2, deep charcoal and forest green with a little coral. The scene is a physical architectural paper model of a small software product represented as a simple house on the left that has grown into a bewildering cluster of many attached little rooms, tangled cables and stacked scaffolds on the right. Human-scale approachable, elegant cut-paper and matte 3D architectural photography aesthetic, dramatic but restrained, natural shadows, no people. Make the main architectural object occupy the right two thirds; leave the upper left third almost empty ivory for slide text. No words, no letters, no numbers, no labels, no logos, no watermark. This is a conceptual metaphor for accidental complexity, not a real product or a chart. Landscape canvas, presentation-ready, polished rather than cartoonish.

### `dashboard-comparison.png`

Prompt:

> Use case: ui-mockup. Asset: a synthetic teaching illustration for a product-management presentation, two app screenshots side by side on a plain warm ivory background. Landscape 16:9, ultra crisp, professional attractive browser-app design with ivory white, dark charcoal and forest green accents. Two separate equally sized realistic browser windows with a modest gap. Both show the same simple fictional expenses dashboard, not a real company or existing product. LEFT window: heading Expenses, two rows Research 100 and Software 200, total 300. Very sparse unfinished interface, NO month selector and NO export button. RIGHT window: heading Expenses, visible dropdown January at upper left of table, a prominent forest-green Export CSV button at upper right, two rows Research 100 and Software 200, Total 300, a subtle green status text Checks passed below. Both interfaces have exactly the same visual style, spacing and column alignment. No captions above or below, no claims about timing or accuracy, no external brands, no real user data, no watermarks, no decorative illustrations. All UI text must be legible and spelled exactly as requested. Maximize the two windows within the landscape canvas. These are intentionally synthetic mock screenshots comparing missing and specified requirements.

### `planning-chat.png`

Prompt:

> Use case: ui-mockup. Generate a crisp, highly legible synthetic screenshot of a fictional AI coding assistant conversation for an educational presentation. Wide 16:9 canvas. Warm white background, dark charcoal text, forest green accent, clean refined desktop app, sparse interface, large fonts, no logos or real product names. Header at top left: Example agent session. A clear forest green mode indicator below the header reads Planning mode. Three large chat bubbles with generous spacing, all text exactly: USER: I want an expenses dashboard. Ask the questions needed to resolve ambiguity. Do not implement yet. AGENT: Should Export CSV use the selected month filter? USER: Yes. Export only the selected month. At the bottom a small status reads Plan ready for review. Include only this short conversation, no other sidebars, no code, no invented performance stats. Make it visually realistic like a polished app screenshot with good typography. This is a fictional teaching mockup, not a real Codex or Claude session.

### `save-chat.png`

Prompt:

> Use case: ui-mockup. Generate a crisp, highly legible synthetic screenshot of a fictional AI coding assistant for an educational presentation. Wide 16:9. Warm white background, dark charcoal, forest green accents, clean professional desktop UI, large fonts, no brand logos. Header: Example agent session. Left two-thirds show two short chat bubbles with exact text: USER: Save the plan, decisions, checks and next step to HANDOVER.md. AGENT: Saved HANDOVER.md. Next session: read this file before continuing. Right third is a simple document preview headed HANDOVER.md containing four short lines: Plan / Decisions / Checks / Next step. Below them a small green Saved label. Spacious composition, sharp readable text, no extra messages, no technical logs, no claims about benchmark outcomes. This is a fictional teaching mockup, not a real Codex or Claude session.

## Editable visuals

The personal feature-diff chart, normalized pilot charts, context/compaction diagram and workflow are native HTML/SVG. They remain editable. The personal examples concern different features; the context percentages are diagram values, not measured product thresholds. The numerical pilot inputs remain exact in `index.html` even though the main slide rounds percentages.
