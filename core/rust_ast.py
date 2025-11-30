# Rust AST Classes for Code Generation
"""
Lightweight Rust AST representation for type-safe code generation.
This provides structure and validation before string generation.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum


class BinaryOp(Enum):
    """Binary operators in Rust"""
    Add = "+"
    Sub = "-"
    Mul = "*"
    Div = "/"
    Rem = "%"
    And = "&&"
    Or = "||"
    Eq = "=="
    Ne = "!="
    Lt = "<"
    Le = "<="
    Gt = ">"
    Ge = ">="


class UnaryOp(Enum):
    """Unary operators in Rust"""
    Neg = "-"
    Not = "!"


# ============================================================================
# Expression AST Nodes
# ============================================================================

@dataclass
class RustExpr:
    """Base class for all Rust expressions"""
    pass


@dataclass
class Literal(RustExpr):
    """Literal value: 42.0_f64, true, "hello" """
    value: Union[float, int, bool, str]
    type_hint: Optional[str] = None  # e.g., "_f64"
    
    def __str__(self):
        if isinstance(self.value, float):
            return f"{self.value}_f64"
        elif isinstance(self.value, bool):
            return str(self.value).lower()
        elif isinstance(self.value, str):
            return f'"{self.value}"'
        return str(self.value)


@dataclass
class Identifier(RustExpr):
    """Variable or parameter name: x, velocity, BW"""
    name: str
    
    def __str__(self):
        return self.name


@dataclass
class BinaryExpr(RustExpr):
    """Binary operation: left op right"""
    left: RustExpr
    op: BinaryOp
    right: RustExpr
    
    def __str__(self):
        return f"({self.left} {self.op.value} {self.right})"


@dataclass
class UnaryExpr(RustExpr):
    """Unary operation: -x, !condition"""
    op: UnaryOp
    expr: RustExpr
    
    def __str__(self):
        return f"{self.op.value}{self.expr}"


@dataclass
class MethodCall(RustExpr):
    """Method call: x.powi(2), base.sqrt()"""
    receiver: RustExpr
    method: str
    args: List[RustExpr]
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.receiver}.{self.method}({args_str})"


@dataclass
class FunctionCall(RustExpr):
    """Function call: sqrt(x), safe_div(a, b)"""
    name: str
    args: List[RustExpr]
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.name}({args_str})"


@dataclass
class IfExpr(RustExpr):
    """If expression: if cond { then_val } else { else_val }"""
    condition: RustExpr
    then_branch: RustExpr
    else_branch: Optional[RustExpr] = None
    
    def __str__(self):
        result = f"if {self.condition} {{ {self.then_branch} }}"
        if self.else_branch:
            result += f" else {{ {self.else_branch} }}"
        return result


@dataclass
class IndexExpr(RustExpr):
    """Array indexing: arr[i], y[0]"""
    array: RustExpr
    index: RustExpr
    
    def __str__(self):
        return f"{self.array}[{self.index}]"


# ============================================================================
# Statement AST Nodes
# ============================================================================

@dataclass
class RustStmt:
    """Base class for all Rust statements"""
    pass


@dataclass
class LetStmt(RustStmt):
    """Let binding: let x = value; or let x: type = value;"""
    name: str
    value: RustExpr
    type_annotation: Optional[str] = None
    mutable: bool = False
    
    def __str__(self):
        mut = "mut " if self.mutable else ""
        type_ann = f": {self.type_annotation}" if self.type_annotation else ""
        return f"let {mut}{self.name}{type_ann} = {self.value};"


@dataclass
class Assignment(RustStmt):
    """Assignment: x = value; or arr[i] = value;"""
    target: Union[Identifier, IndexExpr]
    value: RustExpr
    
    def __str__(self):
        return f"{self.target} = {self.value};"


@dataclass
class ExprStmt(RustStmt):
    """Expression as statement"""
    expr: RustExpr
    
    def __str__(self):
        return f"{self.expr};"


# ============================================================================
# Type Nodes
# ============================================================================

@dataclass
class Type:
    """Rust type representation"""
    name: str
    generic_args: Optional[List['Type']] = None
    
    def __str__(self):
        if self.generic_args:
            args = ", ".join(str(arg) for arg in self.generic_args)
            return f"{self.name}<{args}>"
        return self.name


# Common types
class Types:
    F64 = Type("f64")
    I32 = Type("i32")
    BOOL = Type("bool")
    STRING = Type("String")
    
    @staticmethod
    def vec(elem_type: Type) -> Type:
        return Type("Vec", [elem_type])
    
    @staticmethod
    def option(elem_type: Type) -> Type:
        return Type("Option", [elem_type])


# ============================================================================
# Code Generator from AST
# ============================================================================

class RustASTCodeGenerator:
    """Generate Rust code from AST with proper formatting"""
    
    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size
        self.indent_level = 0
    
    def generate(self, node: Union[RustExpr, RustStmt, List]) -> str:
        """Generate Rust code from AST node(s)"""
        if isinstance(node, list):
            return "\n".join(self.generate(n) for n in node)
        
        # Use __str__ for simple nodes
        if isinstance(node, (RustExpr, RustStmt)):
            return self._indent() + str(node)
        
        return str(node)
    
    def _indent(self) -> str:
        return " " * (self.indent_level * self.indent_size)
    
    def indent(self):
        """Increase indentation level"""
        self.indent_level += 1
    
    def dedent(self):
        """Decrease indentation level"""
        self.indent_level = max(0, self.indent_level - 1)


# ============================================================================
# SymPy to Rust AST Transformer
# ============================================================================

import sympy

class SymPyToRustAST:
    """Transform SymPy expressions to Rust AST"""
    
    def transform(self, expr) -> RustExpr:
        """Main transformation method"""
        # Handle numbers
        if isinstance(expr, sympy.Number):
            return Literal(float(expr))
        
        # Handle symbols (variables)
        if isinstance(expr, sympy.Symbol):
            return Identifier(str(expr))
        
        # Handle binary operations
        if isinstance(expr, sympy.Add):
            return self._transform_add(expr)
        
        if isinstance(expr, sympy.Mul):
            return self._transform_mul(expr)
        
        if isinstance(expr, sympy.Pow):
            return self._transform_pow(expr)
        
        # Handle functions
        if isinstance(expr, sympy.Function):
            return self._transform_function(expr)
        
        # Handle piecewise
        if isinstance(expr, sympy.Piecewise):
            return self._transform_piecewise(expr)
        
        # Fallback
        raise NotImplementedError(f"Cannot transform {type(expr)}: {expr}")
    
    def _transform_add(self, expr: sympy.Add) -> RustExpr:
        """Transform addition/subtraction"""
        result = self.transform(expr.args[0])
        for arg in expr.args[1:]:
            # Check if this is subtraction (arg is negative)
            if isinstance(arg, sympy.Mul) and arg.args[0] == -1:
                # Subtraction
                result = BinaryExpr(result, BinaryOp.Sub, self.transform(-arg))
            else:
                # Addition
                result = BinaryExpr(result, BinaryOp.Add, self.transform(arg))
        return result
    
    def _transform_mul(self, expr: sympy.Mul) -> RustExpr:
        """Transform multiplication/division"""
        result = self.transform(expr.args[0])
        for arg in expr.args[1:]:
            if isinstance(arg, sympy.Pow) and arg.exp == -1:
                # Division
                result = BinaryExpr(result, BinaryOp.Div, self.transform(arg.base))
            else:
                # Multiplication
                result = BinaryExpr(result, BinaryOp.Mul, self.transform(arg))
        return result
    
    def _transform_pow(self, expr: sympy.Pow) -> RustExpr:
        """Transform power operations"""
        base = self.transform(expr.base)
        exp = expr.exp
        
        # Check if exponent is integer
        if exp.is_integer:
            exp_val = int(exp)
            # Use .powi() for integer exponents
            return MethodCall(base, "powi", [Literal(exp_val, "")])
        else:
            # Use .powf() for float exponents
            exp_ast = self.transform(exp)
            return MethodCall(base, "powf", [exp_ast])
    
    def _transform_function(self, expr: sympy.Function) -> RustExpr:
        """Transform function calls"""
        func_name = expr.func.__name__.lower()
        args = [self.transform(arg) for arg in expr.args]
        
        # Map SymPy functions to Rust
        func_map = {
            'sqrt': 'sqrt',
            'exp': 'exp',
            'log': 'ln',
            'sin': 'sin',
            'cos': 'cos',
            'tan': 'tan',
            'abs': 'abs',
        }
        
        rust_func = func_map.get(func_name, func_name)
        
        # Most math functions are methods on f64
        if rust_func in ['sqrt', 'exp', 'ln', 'sin', 'cos', 'tan', 'abs']:
            return MethodCall(args[0], rust_func, [])
        else:
            return FunctionCall(rust_func, args)
    
    def _transform_piecewise(self, expr: sympy.Piecewise) -> RustExpr:
        """Transform piecewise to if-else chain"""
        result = None
        
        for i, (val, cond) in enumerate(expr.args):
            val_ast = self.transform(val)
            
            if i == len(expr.args) - 1 and cond == True:
                # Final else branch
                if result is None:
                    result = val_ast
                else:
                    result = IfExpr(result.condition, result.then_branch, val_ast)
            else:
                # If or else-if branch
                cond_ast = self._transform_condition(cond)
                if result is None:
                    result = IfExpr(cond_ast, val_ast)
                else:
                    # Nest into else branch
                    new_if = IfExpr(cond_ast, val_ast)
                    result = IfExpr(result.condition, result.then_branch, new_if)
        
        return result
    
    def _transform_condition(self, cond) -> RustExpr:
        """Transform boolean conditions"""
        if isinstance(cond, sympy.Rel):
            left = self.transform(cond.lhs)
            right = self.transform(cond.rhs)
            
            op_map = {
                sympy.Eq: BinaryOp.Eq,
                sympy.Ne: BinaryOp.Ne,
                sympy.Lt: BinaryOp.Lt,
                sympy.Le: BinaryOp.Le,
                sympy.Gt: BinaryOp.Gt,
                sympy.Ge: BinaryOp.Ge,
            }
            
            op = op_map.get(type(cond))
            return BinaryExpr(left, op, right)
        
        return self.transform(cond)
