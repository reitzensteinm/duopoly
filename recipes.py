from dataclasses import dataclass
from typing import List


@dataclass
class Recipe:
    id: int
    description: str
    prompt: str


recipes_list: List[Recipe] = []


def create_recipe(id: int, description: str, prompt: str):
    recipe = Recipe(id, description, prompt)
    recipes_list.append(recipe)
