import sys
import os
from pathlib import Path
import json

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent import TeachingVideoAgent, RunConfig, get_api_and_output

# Configuration
folder_prefix = "TEST-single-REGEN-BS"
knowledge_point = "Binary Search"
api_name = "claude"

# Mock API
def mock_api(*args, **kwargs): return None

# Initialize Agent
_, folder_name = get_api_and_output(api_name)
folder = Path(__file__).resolve().parent / "CASES" / f"{folder_prefix}_{folder_name}"

agent = TeachingVideoAgent(
    idx=0,
    knowledge_point=knowledge_point,
    folder=folder,
    cfg=RunConfig(api=mock_api)
)

print(f"Output Dir: {agent.output_dir}")

# Load sections
storyboard_file = agent.output_dir / "storyboard.json"
if not storyboard_file.exists():
    print("Storyboard not found!")
    sys.exit(1)

with open(storyboard_file, "r", encoding="utf-8") as f:
    storyboard_data = json.load(f)

from agent import Section
agent.sections = []
for section_data in storyboard_data["sections"]:
    section = Section(
        id=section_data.get("id", "unknown"),
        title=section_data.get("title", "Untitled"),
        lecture_lines=section_data.get("lecture_lines", []),
        animations=section_data.get("animations", []),
    )
    agent.sections.append(section)

# Search for all MP4s
print("Searching for MP4 files...")
mp4_files = list(agent.output_dir.rglob("*.mp4"))
print(f"Found {len(mp4_files)} MP4 files:")
for f in mp4_files:
    print(f" - {f}")

# Map sections to files
for section in agent.sections:
    # Logic to match section.id to filename
    # section.id: section_0_intro_part1
    # expected filename: Section0IntroPart1Scene.mp4 or section_0_intro_part1.mp4
    
    candidates = []
    candidates.append(f"{section.id}.mp4")
    candidates.append(f"{section.id}_optimized.mp4")
    candidates.append(f"{section.id.title().replace('_', '')}Scene.mp4")
    
    for mp4 in mp4_files:
        if mp4.name in candidates:
            agent.section_videos[section.id] = str(mp4)
            print(f"Matched {section.id} -> {mp4}")
            break

print(f"Matched {len(agent.section_videos)} out of {len(agent.sections)} sections.")

if agent.section_videos:
    final = agent.merge_videos(output_filename="Binary_Search_Forced_Merge.mp4")
    print(f"Merge result: {final}")
else:
    print("No videos matched, cannot merge.")
