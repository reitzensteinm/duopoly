from dataclasses import dataclass
from typing import List


@dataclass
class Recipe:
    id: str
    description: str
    prompt: str


recipes_list: List[Recipe] = []


def create_recipe(id: str, description: str, prompt: str):
    recipe = Recipe(id, description, prompt)
    recipes_list.append(recipe)


MOVE = """To move code from one file to another, the following steps must be taken: 
 * Delete the code in the source file
 * Add the code in the destination file 
 * Delete any unused imports in the source file
 * Add any imports required in the destination file
 * Add an import to the source file to be able to call the code in the destination file"""

create_recipe("MOVE", "Move code between files", MOVE)
