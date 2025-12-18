import os


def get_prompt3_code(regenerate_note, section, base_class):
    return f"""
You are an expert Manim animator using Manim Community Edition v0.19.0. 
Please generate a high-quality Manim class based on the following teaching script.
{regenerate_note}

1. Basic Requirements:
- Use the provided TeachingScene base class without modification.
- **CHINESE SUPPORT (CRITICAL)**: 
  - Any text displayed on screen (labels, titles, explanations) MUST be in Simplified Chinese.
  - **FONT SETTING**: When creating `Text` objects containing Chinese, YOU MUST SPECIFY A FONT that supports Chinese.
  - **Example**: `Text("二分查找", font="Microsoft YaHei", font_size=24)` or `Text("你好", font="SimHei")`.
  - Do NOT use `Tex` or `MathTex` for Chinese characters unless you are sure the LaTeX environment supports it (safest to use `Text` with font).

2. Animation Quality & Smoothness:
- **Timing**: Set appropriate `run_time` (default is often too fast). Use `run_time=1.0` or `1.5` for clear visibility.
- **Transitions**: Prefer `TransformMatchingShapes` or `ReplacementTransform` for fluid changes.
- **Color**: Use the `animate` syntax for smooth color changes (e.g., `obj.animate.set_color(RED)`).

3. Visual Anchor System (MANDATORY):
- Use 6x6 grid system (A1-F6) for precise positioning.
- All labels must be positioned within 1 grid unit of their corresponding objects
- Grid layout (right side only):
lecture |  A1  A2  A3  A4  A5  A6
        |  B1  B2  B3  B4  B5  B6
        |  C1  C2  C3  C4  C5  C6
        |  D1  D2  D3  D4  D5  D6
        |  E1  E2  E3  E4  E5  E6
        |  F1  F2  F3  F4  F5  F6

4. POSITIONING METHODS:
- Point example: self.place_at_grid(obj, 'B2', scale_factor=0.8)
- Area example: self.place_in_area(obj, 'A1', 'C3', scale_factor=0.7)
- NEVER use .to_edge(), .move_to(), or manual positioning!

5. TEACHING CONTENT:
- Title: {section.title}
- Lecture Lines: {section.lecture_lines}
- Animation Description: {'; '.join(section.animations)}

6. STRUCTURE FOR CODE:
Use the following comment format to indicate which block corresponds to which line:
# === Animation for Lecture Line 1 ===

7. EXAMPLE STRUCTURE:
```python
from manim import *

{base_class}

class {section.id.title().replace('_', '')}Scene(TeachingScene):
    def construct(self):
        # The title and lecture_lines will be passed in Chinese
        self.setup_layout("{section.title}", {section.lecture_lines})
        
        # rest of animation code
        # === Animation for Lecture Line 1 ===
        # Example of Chinese Text
        # label = Text("目标值", font="Microsoft YaHei", font_size=24, color=YELLOW)
        ...
```

8. MANDATORY CONSTRAINTS:
- Colors: Use light, distinguishable hexadecimal colors.
- Scaling: Maintain appropriate font sizes and object scales for readability.
- Consistency: Do not apply any animation to the lecture lines except for color changes; The lecture lines and title's size and position must remain unchanged.
- Assets: If provided, MUST use the elements in the Animation Description formatted as [Asset: XXX/XXX.png] (abstract path).
- Simplicity: Avoid 3D functions, complex panels, or external dependencies except for filenames in Animation Description.
"""

def get_regenerate_note(attempt, MAX_REGENERATE_TRIES):
    return f"""    
**IMPORTANT NOTE:** This is attempt {attempt}/{MAX_REGENERATE_TRIES} to generate working code.
The previous attempts failed to run correctly. Please:
1. Use only basic, well-tested Manim functions
2. Avoid complex animations that might cause errors
3. Use simple, reliable Manim patterns
"""