import json
from pathlib import Path

def generate_outline():
    base_path = Path("CASES/BinarySearch_Final_Run_CLAUDE/0-二分搜索")
    base_path.mkdir(parents=True, exist_ok=True)
    outline_file = base_path / "outline.json"
    
    outline_data = {
        "topic": "二分搜索：从直觉到代码",
        "target_audience": "具备基础编程能力的开发者",
        "data_case_definition": "数组 arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]，target = 23",
        "algorithm_components": ["Array", "Pointers (low, high, mid)"],
        "sections": [
            {
                "id": "section_0_intro",
                "title": "场景引入：查字典的智慧",
                "content": "想象一本1000页的英汉字典，你要找单词'Python'。线性查找是从第1页翻到第1000页，最坏情况需要翻遍全书。而二分查找是直接翻到中间（第500页），发现'P'在'M'后面，于是前半本直接丢弃。重复此过程，每次排除一半，只需约10次就能找到。这就是二分搜索的核心：分而治之。",
                "visual_suggestion": "展示书本逐页翻阅与直接折半查找的对比动画。",
                "code_mapping": "None"
            },
            {
                "id": "section_1_core_idea",
                "title": "核心思想与前提",
                "content": "二分搜索的核心在于每次迭代排除一半的可能性。但有一个绝对前提：数据必须是有序的（Sorted）。如果数据无序，无法判断目标在哪一半，二分搜索失效。",
                "visual_suggestion": "展示有序数组与无序数组的对比，无序数组上二分失败。",
                "code_mapping": "None"
            },
            {
                "id": "section_2_code_setup",
                "title": "代码初始化：三指针登场",
                "content": "我们定义三个指针：low 指向区间头部（索引0），high 指向区间尾部（索引n-1），mid 指向中间。初始状态下，low=0, high=9。",
                "visual_suggestion": "高亮显示 low, high, mid 指针在数组上的位置。",
                "code_mapping": "low = 0\nhigh = len(arr) - 1"
            },
            {
                "id": "section_3_iteration_1",
                "title": "迭代 1：向右逼近",
                "content": "计算 mid = (0+9)//2 = 4，arr[4] = 16。目标 target = 23。因为 16 < 23，说明目标在右半部分。更新 low = mid + 1 = 5。",
                "visual_suggestion": "显示比较过程，将左半部分变灰排除，low 指针移动。",
                "code_mapping": "mid = (low + high) // 2\nif arr[mid] < target:\n    low = mid + 1"
            },
            {
                "id": "section_4_iteration_2",
                "title": "迭代 2：向左收缩",
                "content": "新区间 [5, 9]。计算 mid = (5+9)//2 = 7，arr[7] = 56。56 > 23，说明目标在左半部分。更新 high = mid - 1 = 6。",
                "visual_suggestion": "显示比较过程，将右半部分变灰排除，high 指针移动。",
                "code_mapping": "elif arr[mid] > target:\n    high = mid - 1"
            },
            {
                "id": "section_5_iteration_3",
                "title": "迭代 3：命中目标",
                "content": "新区间 [5, 6]。计算 mid = (5+6)//2 = 5，arr[5] = 23。23 == 23，找到目标！返回索引 5。",
                "visual_suggestion": "显示比较成功，高亮目标元素，返回结果。",
                "code_mapping": "else:\n    return mid"
            },
            {
                "id": "section_6_not_found",
                "title": "查找失败：指针交错",
                "content": "如果要找 target=100（不存在）。low 会不断右移，直到 low > high。此时循环终止，返回 -1。这是判断元素不存在的标准。",
                "visual_suggestion": "演示查找不存在元素的过程，最终 low 跑到 high 右边。",
                "code_mapping": "while low <= high:\n...\nreturn -1"
            },
             {
                "id": "section_7_complexity",
                "title": "复杂度分析",
                "content": "每次操作搜索区间减半，直到区间大小为1。假设经过k次，n/2^k = 1，即 k = log2(n)。时间复杂度为 O(log n)。相比 O(n) 的线性查找，效率提升巨大。",
                "visual_suggestion": "展示 log n 曲线与 n 曲线的对比。",
                "code_mapping": "None"
            },
            {
                "id": "section_8_summary",
                "title": "总结",
                "content": "二分搜索是处理有序数据的高效工具。关键点：1. 数组必须有序。2. 循环条件 low <= high。3. 指针更新 mid+1 / mid-1。掌握这些，你就能在海量数据中瞬间定位目标。",
                "visual_suggestion": "总结关键点清单。",
                "code_mapping": "None"
            },
            {
                "id": "section_9_full_code",
                "title": "完整代码展示",
                "content": "这是二分搜索的完整 Python 实现代码。",
                "visual_suggestion": "全屏展示完整代码。",
                "code_mapping": "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1"
            }
        ]
    }

    with open(outline_file, "w", encoding="utf-8") as f:
        json.dump(outline_data, f, ensure_ascii=False, indent=2)
    
    print(f"Generated outline at {outline_file}")

if __name__ == "__main__":
    generate_outline()
