# AI Artifact Generation Template

This template allows you to define artifacts for automated generation across multiple AI platforms (ChatGPT, Gemini, Claude).

## Template Format

Each artifact should be defined with the following metadata:

```markdown
### [Artifact Name]
**Type:** [image|text|code|other]
**Provider:** [gemini|chatgpt|claude]
**Output Name:** [filename without extension]
**Extension:** [png|jpg|txt|md|etc]

[Your prompt here]
```

---

## Example: Image Generation

### Fantasy Sword Icon
**Type:** image
**Provider:** gemini
**Output Name:** fantasy_sword_icon
**Extension:** png

```
Create a pixel art style fantasy sword icon with a blue glowing blade, golden hilt with red gems, and magical sparkles around it. 64x64 pixels, transparent background.
```

### Healing Potion
**Type:** image
**Provider:** gemini
**Output Name:** healing_potion
**Extension:** png

```
Create a game item icon of a round glass potion bottle filled with bright red liquid. Cork stopper on top. Small heart symbol embossed on the glass. Glowing magical effect. Cartoonish style, clean lines, vibrant colors. 64x64px icon size.
```

---

## Example: Text Generation

### Product Description
**Type:** text
**Provider:** chatgpt
**Output Name:** product_description
**Extension:** txt

```
Write a compelling product description for a smart home security camera with AI detection, 4K resolution, and night vision capabilities. Keep it under 150 words, highlight key benefits.
```

---

## Example: Code Generation

### React Component
**Type:** code
**Provider:** claude
**Output Name:** button_component
**Extension:** tsx

```
Create a reusable React TypeScript button component with variants (primary, secondary, danger), sizes (small, medium, large), loading state, and disabled state. Include proper TypeScript types and styled-components.
```

---

## Notes

- **Type**: Defines what kind of artifact is being generated
  - `image`: Image generation (supports Gemini, ChatGPT with DALL-E)
  - `text`: Text content generation
  - `code`: Code generation
  - `other`: Other artifact types

- **Provider**: Which AI service to use
  - `gemini`: Google Gemini (best for Imagen image generation)
  - `chatgpt`: OpenAI ChatGPT (DALL-E for images, GPT for text/code)
  - `claude`: Anthropic Claude (best for code and text)

- **Output Name**: The base filename for the generated artifact (without extension)

- **Extension**: File extension for the output (png, jpg, txt, md, tsx, etc.)

- The prompt should be clear, detailed, and self-contained

- For images, include style, colors, size, and background preferences

- Multiple artifacts can be defined in a single file
