import json


def get_prompt2_storyboard(outline, reference_image_path):
    # --- 修改开始：在开头加入强制中文指令，并优化动画要求 ---
    base_prompt = f""" 
    You are a professional education Explainer and Animator, expert at converting mathematical teaching outlines into storyboard scripts suitable for the Manim animation system.

    # IMPORTANT: LANGUAGE REQUIREMENT
    # ALL OUTPUTS MUST BE IN SIMPLIFIED CHINESE (简体中文).
    # The lecture lines must be natural, spoken Chinese.

    ## Task
    Convert the following teaching outline into a detailed step-by-step storyboard script:

    {outline}
    """

    # Add reference image guidance (保持不变)
    if reference_image_path:
        base_prompt += f"""
    ## Reference Image Available
    A reference image has been provided to assist with designing the animations for this concept.
    ... (此处省略 reference image 的中间内容，保持原样即可) ...
    """

    # --- 修改重点：优化 Storyboard Requirements ---
    base_prompt += """
    ## Storyboard Requirements
    
    ### Content Structure
    - For key sections (max 3 sections), use up to 5 lecture lines along with their corresponding 5 animations.
    - Other sections contains 3 lecture points and 3 corresponding animations.
    - **Language**: All `title` and `lecture_lines` MUST be in Simplified Chinese.
    - **Brevity**: Keep lecture lines concise (Max 20 Chinese characters per line).
    - **Flow**: Ensure a smooth logical flow between steps.

    ### Visual Design
    - Colors: Background fixed at #000000. Use professional, high-contrast color palettes (e.g., #89CFF0 for focus, #FFFFFF for text).
    - Element Labeling: Assign clear labels in Chinese near all elements.

    ### Animation Effects (CRITICAL FOR QUALITY)
    - **Smoothness**: Avoid rapid flashing or "ghostly" jittering. Use smooth interpolations (e.g., `run_time=1.5` for complex moves).
    - **Transitions**: Use `Transform`, `ReplacementTransform`, or `Write` for smooth transitions between states. Avoid simply `FadeIn`/`FadeOut` for everything.
    - **Sync**: Animation steps must closely correspond to the meaning of the lecture points.

    ### Constraints
    - No panels or 3D methods.
    - Focus animations on visualizing concepts that are difficult to grasp from lecture lines alone.
    - Do not involve any external elements (SVGs/assets) unless specified.

    MUST output the storyboard design in JSON format:
    {{
        "sections": [
            {{
                "id": "section_1",
                "title": "Sec 1: 章节标题(中文)",
                "lecture_lines": ["第一句讲解词", "第二句讲解词", ...],
                "animations": [
                    "Animation step 1: (Describe the visual action in English or Chinese)",
                    ...
                ]
            }},
            ...
        ]
    }}
    """
    return base_prompt


def get_prompt_download_assets(storyboard_data):
    return f"""
Analyze this educational video storyboard and identify at most 4 different ESSENTIAL visual elements that MUST be represented with downloadable icons/images (not manually drawn shapes).

Content:
{storyboard_data}

Selection Criteria:
1. Only choose elements that appear in **introduction** or **application** sections, and that are:
   - Real-world, recognizable physical objects
   - Visually distinctive enough that a generic shape would not be sufficient
   - Concrete, not abstract concepts
2. Prioritize: specific animals, characters, vehicles, tools, devices, landmarks, everyday objects
3. IGNORE and NEVER include:
   - Abstract concepts (e.g., justice, communication)
   - Symbols or icons for ideas (e.g., letters, formulas, diagrams, trees in data structure)
   - Geometric shapes, arrows, or math-related visuals
   - Any object composed entirely of basic shapes without unique visual identity

Output format:
- Output ONLY the object keywords, each keyword must be one word, one per line, all lowercase, no numbering, no extra text.
"""


def get_prompt_place_assets(asset_mapping, animations_structure):
    return f"""
You need to enhance only the animations by incorporating downloaded assets where appropriate.

Asset list:
{asset_mapping}

Current Animations Data:
{animations_structure}

Instructions:
- For each animation, determine if any downloaded assets should be incorporated.
- Only choose the most relevant asset for the animation step that needs.
- Insert the **abstract path** of asset in the form: [Asset: XXX].
- CAN ONLY use the assets in **THE FIRST and THE LAST** sections.
- Keep the same structure: return an array with section_index, section_id, and enhanced animations.
- Only modify the animation descriptions to include asset references.
- Do not change section_index or section_id.

Return only the enhanced animations data as valid JSON array:
"""
