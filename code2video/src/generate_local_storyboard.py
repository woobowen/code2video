import json
from pathlib import Path

def generate_storyboard():
    # Path to outline
    base_path = Path("CASES/BinarySearch_Final_Run_CLAUDE/0-二分搜索")
    outline_file = base_path / "outline.json"
    storyboard_file = base_path / "storyboard.json"

    if not outline_file.exists():
        print(f"Outline not found at {outline_file}")
        return

    with open(outline_file, "r", encoding="utf-8") as f:
        outline = json.load(f)

    storyboard_sections = []
    
    for section in outline["sections"]:
        # Simple heuristic to split content into lines
        content = section["content"]
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        animations = []
        animations.append(f"Setup Layout: Standard split layout. Title: '{section['title']}'")
        
        # Check if code mapping exists to decide layout hint
        if section.get("code_mapping") and section["code_mapping"] != "None":
             animations.append("Layout: Split-Left (Code Bottom-Left, Text Top-Left)")
        else:
             animations.append("Layout: Standard (Text Left, Visual Right)")

        visual = section.get("visual_suggestion", "Visual representation of the concept")
        animations.append(f"Visual Action: {visual}")
        
        chunk_size = 3
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i+chunk_size]
            text = " ".join(chunk)
            animations.append(f"Show Text: Display '{text}' in lecture notes area.")

        storyboard_sections.append({
            "id": section["id"],
            "title": section["title"],
            "lecture_lines": lines,
            "animations": animations
        })

    storyboard_data = {"sections": storyboard_sections}

    with open(storyboard_file, "w", encoding="utf-8") as f:
        json.dump(storyboard_data, f, ensure_ascii=False, indent=2)
    
    print(f"Generated storyboard at {storyboard_file}")

if __name__ == "__main__":
    generate_storyboard()
