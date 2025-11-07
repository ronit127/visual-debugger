from dataclasses import dataclass, field
from typing import List

from dataclasses import dataclass
from typing import Any

@dataclass
class Operation:
    effect: str = ""                 # e.g. "Add", "Remove"
    method: str = ""                # e.g. "append", "pop", "insert"
    line_num: int = -1
    params: list[Any] = field(default_factory=list) # e.g. [5], or ["key", "value"]
    index: Any = None
    

@dataclass
class ErrorClass:
    name: str
    line_num: int
    error_msg: str

@dataclass
class VariableData:
    name: str
    var_type: str
    operations: List[Operation] = field(default_factory=list)
    errors: List[ErrorClass] = field(default_factory=list)

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other