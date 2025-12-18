import os

def get_prompt3_code(regenerate_note, section, base_class):
    return f"""
你是一位精通 Manim Community Edition v0.19.0 的动画代码专家。
请根据以下脚本生成高质量的 Python 代码。

{regenerate_note}

### 核心规范 (必须严格遵守)

1. **基础类与中文支持**:
   - 继承提供的 `TeachingScene` 类。
   - **中文字体**：所有 `Text` 对象必须指定支持中文的字体。推荐使用 `font="Microsoft YaHei"` 或 `font="SimHei"`。
   - **不要**使用 `Tex` 或 `MathTex` 来渲染纯中文句子（会报错或乱码），仅在渲染数学公式时使用 `MathTex`。

2. **消除“鬼畜”现象 (Anti-Ghosting Guidelines)**:
   - **文字变换**：当文本发生变化时，优先使用 `TransformMatchingShapes(old_text, new_text)` 或 `FadeTransform(old, new)`。不要使用原始 `Transform`。
   - **物体变换**：如果物体形状差异巨大（如 `Square` 变 `Circle`），使用 `ReplacementTransform`。
   - **时间控制**：
     - 标准动作：`run_time=1.0` 到 `1.5`。
     - 复杂推导：`run_time=2.0`。
     - **必须等待**：在每一个动画动作（`self.play(...)`）之后，**必须**添加 `self.wait(1)` 或 `self.wait(2)`，确保观众看清楚。

3. **视觉锚点与布局 (6x6 Grid)**:
   - 使用 `self.place_at_grid(obj, 'B2')` 等方法。
   - 保持布局整洁，不要让文字覆盖图形。

4. **代码结构**:
   - 标题: {section.title}
   - 讲解词 (List): {section.lecture_lines}
   - 动画指令 (List): {section.animations}

   **逻辑对应**：
   - 遍历 `lecture_lines`。
   - 对于每一行讲解词：
     1. 首先：`self.highlight_lecture_line(index)` (假设基类中有此方法，或仅改变颜色)。
     2. 然后：执行对应的动画。
     3. 最后：`self.wait(2)`。

5. **示例代码结构**:
```python
from manim import *

{base_class}

class {section.id.title().replace('_', '')}Scene(TeachingScene):
    def construct(self):
        # 初始化布局
        self.setup_layout("{section.title}", {section.lecture_lines})
        
        # === 第 1 句讲解 ===
        # 1. 高亮左侧文本 (手动模拟)
        self.play(self.lecture[0].animate.set_color(YELLOW), run_time=0.5)
        
        # 2. 执行右侧动画
        circle = Circle(color=BLUE, fill_opacity=0.5)
        self.place_at_grid(circle, 'C3')
        self.play(DrawBorderThenFill(circle), run_time=1.5)
        
        # 3. 留白时间 (CRITICAL)
        self.wait(2)

        # === 第 2 句讲解 ===
        self.play(self.lecture[0].animate.set_color(WHITE), self.lecture[1].animate.set_color(YELLOW), run_time=0.5)
        
        # 更好的变换效果
        square = Square(color=RED, fill_opacity=0.5)
        self.place_at_grid(square, 'C3')
        self.play(ReplacementTransform(circle, square), run_time=1.5)
        
        self.wait(2)
```

6. **强制约束**:
- 颜色使用明亮的 hex 颜色。
- 严禁使用复杂的 3D 场景（除非必要），保持 2D 清晰图解。
- 不要在动画中改变左侧 lecture_lines 的位置或大小，只改变颜色。
"""

def get_regenerate_note (attempt, MAX_REGENERATE_TRIES):
    return f"""注意：这是第 {attempt}/{MAX_REGENERATE_TRIES} 次尝试生成代码。上一次生成的代码运行失败或效果不佳。请：
简化复杂的动画逻辑，优先保证运行成功。
确保所有的变量在使用前都已定义。
检查 self.wait () 是否充足。
"""