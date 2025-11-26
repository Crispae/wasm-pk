# File: sbml_rust_generator/core/base.py
"""Abstract base classes for SBML to Rust code generation pipeline"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Parser(ABC):
    """Abstract base class for expression parsers"""

    @abstractmethod
    def parse(self, expression: str) -> Any:
        """Parse an expression string into an internal representation

        Args:
            expression: The expression string to parse

        Returns:
            Parsed expression in internal format (e.g., SymPy expression)
        """
        pass


class CodeGenerator(ABC):
    """Abstract base class for code generators"""

    @abstractmethod
    def generate(self, expression: Any) -> str:
        """Generate code from an expression

        Args:
            expression: The expression to generate code from

        Returns:
            Generated code as string
        """
        pass


class ModelProcessor(ABC):
    """Abstract base class for model processors"""

    @abstractmethod
    def process(self, model_data: Dict[str, Any]) -> Any:
        """Process model data and return processed result

        Args:
            model_data: Dictionary containing model data

        Returns:
            Processed model result
        """
        pass


class Optimizer(ABC):
    """Abstract base class for expression optimizers"""

    @abstractmethod
    def optimize(self, expressions: List[Any]) -> Any:
        """Optimize a list of expressions

        Args:
            expressions: List of expressions to optimize

        Returns:
            Optimized expressions
        """
        pass
