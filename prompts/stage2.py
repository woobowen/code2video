import json


def get_prompt2_storyboard(outline, reference_image_path):
    base_prompt = f""" 
    你是一位专业的教育视频分镜师和 Manim 动画专家。你的任务是将教学大纲转化为详细的、适合代码生成的逐帧分镜脚本。

    # 重要语言要求
    * 所有输出必须为 **简体中文**。
    * 讲解词（lecture_lines）必须是自然、流畅、**有深度**的口语。

    ## 任务输入
    {outline}
    """

    if reference_image_path:
        base_prompt += f"""
    ## 参考图片
    请参考提供的图片设计动画视觉元素，尽量还原图片中的关键图示结构。
    """

    base_prompt += """
    ## 分镜设计要求 (CRITICAL)

    ### 1. 内容与讲解 (Content)
    - **解释性**：讲解词不要只读定义，要解释“为什么”。允许每行讲解词稍微长一点（建议 20-40 字），把逻辑讲透。
    - **数量**：核心章节（Key Sections）可以使用最多 6-8 组 [讲解词+动画] 的配对，确保节奏不赶。普通章节 3-5 组。

    ### 2. 视觉设计 (Visuals)
    - **背景**：纯黑背景 (#000000)。
    - **配色**：使用高对比度、专业的配色方案（如 Blue, Teal, Yellow），避免使用暗淡的颜色。
    - **布局**：左侧是讲解文本，右侧是 6x6 的动画网格。

    ### 3. 动画质量控制 (防止鬼畜/Ghosting) - 非常重要！
    - **禁止暴力变换**：不要对结构完全不同的物体使用 `Transform`（例如不要直接把一个复杂的公式 Transform 成一个圆形）。这种情况下请使用 `FadeOut` 前者，再 `FadeIn` 后者。
    - **文字变换**：对于文字/公式的推导，明确指明使用 `TransformMatchingTex` 或 `TransformMatchingShapes`。
    - **留白时间**：在每一个动作完成后，必须暗示代码端留有 `wait(1)` 或 `wait(2)` 的时间，给观众思考的空隙。
    - **平滑移动**：对于物体的移动，使用 `run_time=1.5` 或更慢的速度，展现移动轨迹。

    ### 4. 连贯性 (Coherence)
    - **视觉锚点**：如果一个物体在上一行讲解中出现了，且在下一行中仍然相关，**不要清除它**，让它保持在屏幕上或移动到新位置。

    必须输出为以下 JSON 格式：
    {{
        "sections": [
            {{
                "id": "section_1",
                "title": "章节标题",
                "lecture_lines": [
                    "第一句详细的讲解词，解释原理...",
                    "第二句讲解词，引导观众观察右侧..."
                ],
                "animations": [
                    "Animation 1: [详细描述] 创建一个黄色圆圈在 B3 位置。使用 Write 动画。",
                    "Animation 2: [详细描述] 将黄色圆圈平滑移动到 D3，同时显现出轨迹线。避免闪烁。"
                ]
            }},
            ...
        ]
    }}
    """
    return base_prompt


def get_prompt_download_assets(storyboard_data):
    return f"""
分析这份教育视频分镜脚本，识别出最多 4 个**必须**使用下载图标/图片（而非手动绘制形状）来表示的关键视觉元素。

内容 (Content):
{storyboard_data}

选择标准 (Selection Criteria):
1. 仅选择出现在**介绍 (Introduction)** 或 **应用 (Application)** 章节中的元素，且必须满足：
   - 现实世界中可识别的物理对象
   - 视觉特征鲜明，仅用通用几何形状不足以表达
   - 具体的实物，而非抽象概念
2. 优先选择：具体的动物、角色、交通工具、工具、设备、地标、日常物品。
3. **忽略且绝不包含**：
   - 抽象概念（如：正义、交流）
   - 思想的符号或图标（如：字母、公式、图表、数据结构树）
   - 几何形状、箭头或数学相关的视觉元素
   - 任何完全由基本形状组成且无独特视觉身份的物体

输出格式 (Output format):
- **仅输出英文关键词**（为了适配搜索引擎），每个关键词占一行，全小写，无编号，无额外文本。
"""


def get_prompt_place_assets(asset_mapping, animations_structure):
    return f"""
你需要通过插入已下载的素材来增强动画描述。

可用素材列表 (Asset list):
{asset_mapping}

当前动画数据 (Current Animations Data):
{animations_structure}

指令 (Instructions):
- 对于每一个动画步骤，判断是否应该融入已下载的素材。
- 仅为需要的动画步骤选择最相关的一个素材。
- 以此格式插入素材的**抽象路径**：[Asset: XXX]。
- **仅限**在**第一个和最后一个**章节中使用素材。
- 保持结构不变：返回一个包含 section_index, section_id 和 enhanced animations 的 JSON 数组。
- 仅修改动画描述以包含素材引用。
- 不要修改 section_index 或 section_id。

仅返回增强后的动画数据，必须是有效的 JSON 数组格式：
"""
