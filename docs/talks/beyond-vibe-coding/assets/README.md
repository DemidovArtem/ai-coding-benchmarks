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

Generated with the **built-in image_gen tool**, not a CLI/API fallback. The selected PNGs were copied into this directory after visual inspection. They contain no employer data. Houses are conceptual metaphors; dashboard windows are synthetic examples. They are not proof of an application state, browser test or measured outcome. House reuse is intentional across the cover/story/diff sequence requested by the speaker; dashboard reuse supports progressive reveals.

### `coherent-house.png`

Reference: `complexity-house.png`, used only for style. A new coherent building replaces the tangled structure on the cover. The selected built-in output was `exec-bb36de1f-da2b-46c9-9790-134b6e5c2ce9.png`.

Prompt:

> Use case: stylized-concept. Asset type: 16:9 presentation cover and architectural metaphor. Primary request: a beautifully coherent modest house representing a maintainable AI prototype. Reference image is the existing architectural paper-model illustration; match its warm ivory background, tactile cream plaster, dark forest-green doors and window frames, charcoal roof, muted terracotta accent and soft studio lighting. Generate a NEW calm building, not the tangled additions in the reference. One compact two-storey house with two orderly connected volumes, clean rooflines, a small tidy terrace and a short simple path, two small shrubs. No exposed cables, scaffolding, pipes, improvised extensions or chaotic towers. Composition: wide landscape, house fully visible in the RIGHT 55 percent, left 45 percent almost empty warm off-white for slide title. Elegant architectural miniature, warm and inviting, readable silhouette. No words, numbers, logos, borders or watermark.

### `complexity-house.png`

Prompt:

> Use case: illustration-story. Asset: wide 16:9 illustration for an English product-management talk called Beyond Vibe Coding. Create a tasteful editorial illustration, very high quality, sparse warm ivory background #f8f7f2, deep charcoal and forest green with a little coral. The scene is a physical architectural paper model of a small software product represented as a simple house on the left that has grown into a bewildering cluster of many attached little rooms, tangled cables and stacked scaffolds on the right. Human-scale approachable, elegant cut-paper and matte 3D architectural photography aesthetic, dramatic but restrained, natural shadows, no people. Make the main architectural object occupy the right two thirds; leave the upper left third almost empty ivory for slide text. No words, no letters, no numbers, no labels, no logos, no watermark. This is a conceptual metaphor for accidental complexity, not a real product or a chart. Landscape canvas, presentation-ready, polished rather than cartoonish.

### `dashboard-comparison.png`

Prompt:

> Use case: ui-mockup. Asset: a synthetic teaching illustration for a product-management presentation, two app screenshots side by side on a plain warm ivory background. Landscape 16:9, ultra crisp, professional attractive browser-app design with ivory white, dark charcoal and forest green accents. Two separate equally sized realistic browser windows with a modest gap. Both show the same simple fictional expenses dashboard, not a real company or existing product. LEFT window: heading Expenses, two rows Research 100 and Software 200, total 300. Very sparse unfinished interface, NO month selector and NO export button. RIGHT window: heading Expenses, visible dropdown January at upper left of table, a prominent forest-green Export CSV button at upper right, two rows Research 100 and Software 200, Total 300, a subtle green status text Checks passed below. Both interfaces have exactly the same visual style, spacing and column alignment. No captions above or below, no claims about timing or accuracy, no external brands, no real user data, no watermarks, no decorative illustrations. All UI text must be legible and spelled exactly as requested. Maximize the two windows within the landscape canvas. These are intentionally synthetic mock screenshots comparing missing and specified requirements.

## Editable visuals

The normalized pilot and model-cost/index charts, context diagram, goal command, model allocation and workflow are native HTML/SVG. They remain editable. The context meter has qualitative labels, with no numeric compaction threshold. Exact metric inputs remain in `index.html` even though main headlines are rounded.

The two chat examples are native HTML reconstructions of Codex's dark interface conventions, using `codex-plan-ui.png` as a style reference. They are explicitly labelled reconstructed examples, not actual product captures or observed sessions. The earlier generic generated chat PNGs were removed after speaker feedback; their provenance remains in Git history.
