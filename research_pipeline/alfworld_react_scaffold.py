from __future__ import annotations

import re
from pathlib import Path


TASK_FAMILIES = (
    "pick_and_place_simple",
    "pick_and_place_with_movable_recep",
    "pick_clean_then_place_in_recep",
    "pick_cool_then_place_in_recep",
    "pick_heat_then_place_in_recep",
    "pick_two_obj_and_place",
    "look_at_obj_in_light",
)


def task_family_from_gamefile(game_file: str) -> str:
    """Recover the ALFWorld task family from any path below its task directory."""
    for part in reversed(Path(game_file).parts):
        for family in TASK_FAMILIES:
            if part == family or part.startswith(family + "-"):
                return family
    return "unknown"


def extract_task_goal(initial_observation: str) -> str:
    match = re.search(r"Your task is to:\s*(.+?)(?:\n|$)", initial_observation, flags=re.IGNORECASE)
    return match.group(1).strip() if match else "complete the household task"


def _put_example() -> str:
    return """Example trajectory (simple place):
Task: put a mug on a desk.
Observation: You see a closed cabinet 1 and desk 1.
Thought: I need the mug first, so inspect a plausible container.
Action: go to cabinet 1
Observation: cabinet 1 is closed.
Thought: Open it before searching inside.
Action: open cabinet 1
Observation: cabinet 1 contains mug 1.
Thought: Take the mug, then move to the target.
Action: take mug 1 from cabinet 1
Observation: You are holding mug 1.
Thought: The target is desk 1.
Action: go to desk 1
Observation: You are at desk 1.
Thought: Finish by placing the held mug.
Action: put mug 1 in/on desk 1"""


def _clean_example() -> str:
    return """Example trajectory (clean then place):
Task: put a clean apple on a table.
Observation: apple 1 is on countertop 1; sinkbasin 1 and diningtable 1 are reachable.
Thought: Take the apple, clean it at the sink, then place it on the table.
Action: go to countertop 1
Observation: apple 1 is here.
Action: take apple 1 from countertop 1
Observation: You are holding apple 1.
Action: go to sinkbasin 1
Observation: You are at sinkbasin 1.
Action: clean apple 1 with sinkbasin 1
Observation: apple 1 is clean.
Action: go to diningtable 1
Observation: You are at diningtable 1.
Action: put apple 1 in/on diningtable 1"""


def _cool_example() -> str:
    return """Example trajectory (cool then place):
Task: put a cool plate on a shelf.
Observation: plate 1 is on countertop 1; fridge 1 and shelf 1 are reachable.
Thought: Take the plate, cool it using the fridge, then place it on the shelf.
Action: go to countertop 1
Observation: plate 1 is here.
Action: take plate 1 from countertop 1
Observation: You are holding plate 1.
Action: go to fridge 1
Observation: fridge 1 is closed.
Action: cool plate 1 with fridge 1
Observation: plate 1 is cool.
Action: go to shelf 1
Observation: You are at shelf 1.
Action: put plate 1 in/on shelf 1"""


def _heat_example() -> str:
    return """Example trajectory (heat then place):
Task: put a hot potato on a table.
Observation: potato 1 is on countertop 1; microwave 1 and diningtable 1 are reachable.
Thought: Take the potato, heat it with the microwave, then place it on the table.
Action: go to countertop 1
Observation: potato 1 is here.
Action: take potato 1 from countertop 1
Observation: You are holding potato 1.
Action: go to microwave 1
Observation: You are at microwave 1.
Action: heat potato 1 with microwave 1
Observation: potato 1 is hot.
Action: go to diningtable 1
Observation: You are at diningtable 1.
Action: put potato 1 in/on diningtable 1"""


def _two_example() -> str:
    return """Example trajectory (place two objects):
Task: put two pencils on a desk.
Observation: pencil 1 and pencil 2 are on sidetable 1; desk 1 is reachable.
Thought: Move one pencil at a time and remember that two placements are required.
Action: go to sidetable 1
Observation: pencil 1 and pencil 2 are here.
Action: take pencil 1 from sidetable 1
Observation: You are holding pencil 1.
Action: go to desk 1
Observation: You are at desk 1.
Action: put pencil 1 in/on desk 1
Observation: pencil 1 is on desk 1.
Thought: One remains; return for the second pencil.
Action: go to sidetable 1
Observation: pencil 2 is here.
Action: take pencil 2 from sidetable 1
Observation: You are holding pencil 2.
Action: go to desk 1
Observation: You are at desk 1.
Action: put pencil 2 in/on desk 1"""


def _examine_example() -> str:
    return """Example trajectory (look under light):
Task: look at a book under a desk lamp.
Observation: book 1 is on shelf 1; desklamp 1 is on sidetable 1.
Thought: Hold the target object, locate the lamp, turn it on, then place the object where it is illuminated.
Action: go to shelf 1
Observation: book 1 is here.
Action: take book 1 from shelf 1
Observation: You are holding book 1.
Action: go to sidetable 1
Observation: desklamp 1 is here.
Action: use desklamp 1
Observation: desklamp 1 is on.
Action: put book 1 in/on sidetable 1"""


def _movable_example() -> str:
    return """Example trajectory (movable receptacle):
Task: put a spoon in a bowl and place the bowl on a table.
Observation: spoon 1 is on countertop 1; bowl 1 is on shelf 1; diningtable 1 is reachable.
Thought: Put the target object into the movable receptacle first, then carry that receptacle to the final surface.
Action: go to countertop 1
Observation: spoon 1 is here.
Action: take spoon 1 from countertop 1
Observation: You are holding spoon 1.
Action: go to shelf 1
Observation: bowl 1 is here.
Action: put spoon 1 in/on bowl 1
Observation: spoon 1 is in bowl 1.
Thought: Now pick up the filled bowl and carry it to the final target.
Action: take bowl 1 from shelf 1
Observation: You are holding bowl 1 with spoon 1 in it.
Action: go to diningtable 1
Observation: You are at diningtable 1.
Action: put bowl 1 in/on diningtable 1"""


FAMILY_EXAMPLES = {
    "pick_and_place_simple": _put_example(),
    "pick_clean_then_place_in_recep": _clean_example(),
    "pick_cool_then_place_in_recep": _cool_example(),
    "pick_heat_then_place_in_recep": _heat_example(),
    "pick_two_obj_and_place": _two_example(),
    "look_at_obj_in_light": _examine_example(),
    "pick_and_place_with_movable_recep": _movable_example(),
}


def react_scaffold(task_family: str) -> str:
    """A compact task-family ReAct scaffold modeled on the official ALFWorld prompt structure.

    The examples are locally written equivalents rather than copied benchmark trajectories.
    """
    primary = FAMILY_EXAMPLES.get(task_family, _put_example())
    if task_family == "pick_and_place_simple":
        examples = primary
    else:
        examples = primary + "\n\n" + _put_example()
    return (
        "Solve the household task by interleaving brief reasoning and one admissible environment action. "
        "Keep the task goal fixed across every step. Search receptacles systematically, remember what you are holding, "
        "and complete every required transformation before the final placement. Never invent an action. "
        "End every response with exactly one line `Action: <exact admissible command>`.\n\n"
        + examples
    )
