"""Pydantic schemas for extracted Python AST nodes and function slices."""

from typing import List, Optional
from pydantic import BaseModel, Field


class FunctionSlice(BaseModel):
    """Extracted Python function or method slice with context."""

    name: str
    parent_class: Optional[str] = None
    start_line: int
    end_line: int
    parameters: List[str] = Field(default_factory=list)
    return_annotation: Optional[str] = None
    decorators: List[str] = Field(default_factory=list)
    docstring: Optional[str] = None
    source_code: str
    cyclomatic_complexity: int = 1
    has_exceptions: bool = False
    calls: List[str] = Field(default_factory=list)
    is_modified: bool = False
    modified_lines: List[int] = Field(default_factory=list)

    @property
    def qualified_name(self) -> str:
        """Return 'ClassName.method_name' or 'function_name'."""
        if self.parent_class:
            return f"{self.parent_class}.{self.name}"
        return self.name


class FileASTSummary(BaseModel):
    """Summary of Python AST analysis for a single file."""

    file_path: str
    functions: List[FunctionSlice] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    has_syntax_error: bool = False
    syntax_error_message: Optional[str] = None

    @property
    def modified_functions(self) -> List[FunctionSlice]:
        """Return only functions that intersect with the PR diff."""
        return [fn for fn in self.functions if fn.is_modified]

