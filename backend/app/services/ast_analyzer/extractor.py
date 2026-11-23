"""Python AST parser and function slicer for extracting modified functions and complexity."""

import ast
from typing import List, Optional, Set
from backend.app.schemas.ast_nodes import FileASTSummary, FunctionSlice


class CyclomaticComplexityVisitor(ast.NodeVisitor):
    """Calculates McCabe Cyclomatic Complexity of an AST node."""

    def __init__(self):
        self.complexity = 1

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        # Each boolean operator (and, or) adds a decision branch
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


def calculate_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity for a function AST node."""
    visitor = CyclomaticComplexityVisitor()
    visitor.visit(node)
    return visitor.complexity


def extract_function_calls(node: ast.AST) -> List[str]:
    """Collect function and method calls made within an AST node."""
    calls: List[str] = []
    for subnode in ast.walk(node):
        if isinstance(subnode, ast.Call):
            if isinstance(subnode.func, ast.Name):
                calls.append(subnode.func.id)
            elif isinstance(subnode.func, ast.Attribute):
                calls.append(subnode.func.attr)
    return sorted(list(set(calls)))


def format_parameter(arg: ast.arg) -> str:
    """Format an argument name and its type annotation."""
    if arg.annotation:
        try:
            return f"{arg.arg}: {ast.unparse(arg.annotation)}"
        except Exception:
            return arg.arg
    return arg.arg


def analyze_python_source(
    file_path: str,
    source_code: str,
    modified_line_numbers: Optional[Set[int]] = None,
) -> FileASTSummary:
    """Analyze Python source code and extract function slices and complexity.

    Args:
        file_path: Relative or absolute path of the Python file.
        source_code: Complete contents of the Python source file.
        modified_line_numbers: Optional set of 1-based line numbers modified in the PR.

    Returns:
        FileASTSummary containing function slices, classes, and complexity metrics.
    """
    if modified_line_numbers is None:
        modified_line_numbers = set()

    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        return FileASTSummary(
            file_path=file_path,
            has_syntax_error=True,
            syntax_error_message=f"SyntaxError at line {e.lineno}: {e.msg}",
        )

    source_lines = source_code.splitlines(keepends=True)
    functions: List[FunctionSlice] = []
    classes: List[str] = []
    imports: List[str] = []

    # First pass: collect imports and classes
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                imports.append(ast.unparse(node))
            except Exception:
                pass
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    # Function visitor supporting top-level functions and class methods
    def process_function(
        fn_node: ast.AST, parent_class: Optional[str] = None
    ) -> None:
        if not isinstance(fn_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return

        start_line = fn_node.lineno
        end_line = getattr(fn_node, "end_lineno", start_line)

        # Extract parameters
        params: List[str] = []
        for arg in fn_node.args.posonlyargs + fn_node.args.args:
            params.append(format_parameter(arg))
        if fn_node.args.vararg:
            params.append(f"*{format_parameter(fn_node.args.vararg)}")
        for arg in fn_node.args.kwonlyargs:
            params.append(format_parameter(arg))
        if fn_node.args.kwarg:
            params.append(f"**{format_parameter(fn_node.args.kwarg)}")

        # Extract return annotation
        return_ann = None
        if fn_node.returns:
            try:
                return_ann = ast.unparse(fn_node.returns)
            except Exception:
                pass

        # Extract decorators
        decorators: List[str] = []
        for dec in fn_node.decorator_list:
            try:
                decorators.append(ast.unparse(dec))
            except Exception:
                pass

        # Check for exception handling
        has_exceptions = any(
            isinstance(sub, (ast.Try, ast.Raise)) for sub in ast.walk(fn_node)
        )

        # Slice source code lines (1-based to 0-based indexing)
        fn_lines = source_lines[start_line - 1 : end_line]
        fn_source = "".join(fn_lines)

        # Check intersection with modified lines
        fn_line_range = set(range(start_line, end_line + 1))
        intersected_lines = sorted(list(fn_line_range.intersection(modified_line_numbers)))
        is_modified = len(intersected_lines) > 0

        functions.append(
            FunctionSlice(
                name=fn_node.name,
                parent_class=parent_class,
                start_line=start_line,
                end_line=end_line,
                parameters=params,
                return_annotation=return_ann,
                decorators=decorators,
                docstring=ast.get_docstring(fn_node),
                source_code=fn_source,
                cyclomatic_complexity=calculate_complexity(fn_node),
                has_exceptions=has_exceptions,
                calls=extract_function_calls(fn_node),
                is_modified=is_modified,
                modified_lines=intersected_lines,
            )
        )

    # Walk root and classes
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            process_function(node, parent_class=None)
        elif isinstance(node, ast.ClassDef):
            for class_child in ast.iter_child_nodes(node):
                if isinstance(class_child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    process_function(class_child, parent_class=node.name)

    return FileASTSummary(
        file_path=file_path,
        functions=functions,
        classes=classes,
        imports=imports,
        has_syntax_error=False,
    )

