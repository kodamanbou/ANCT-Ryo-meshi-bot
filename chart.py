import dataclasses


@dataclasses.dataclass
class Menu:
    fname: str
    meal_type: int = 0  # 0: breakefast, 1: lunch, 2: dinner
    date: str = None
    x: int = 0
    y: int = 0


@dataclasses.dataclass
class Label:
    fname: str
    value: str = None
    x: int = 0
    y: int = 0
