# File: sbml_rust_generator/symbolic/assignment_processor.py
"""Processes SBML assignment rules with dependency resolution"""

import sympy
from typing import Dict, List, Tuple, Any, Set
from core.base import ModelProcessor
from parsers.expression_parser import SbmlExpressionParser


class AssignmentRuleProcessor(ModelProcessor):
    """Processes assignment rules with topological sorting for dependencies"""

    def __init__(self, parser: SbmlExpressionParser):
        """Initialize assignment rule processor

        Args:
            parser: Expression parser for assignment rule expressions
        """
        self.parser = parser

    def process(self, model_data: Dict[str, Any]) -> List[Tuple[str, sympy.Expr]]:
        """Process assignment rules from model data

        Args:
            model_data: Dictionary containing model data with 'assignmentRules' key

        Returns:
            List of (variable, expression) tuples in dependency order
        """
        assignment_rules = model_data.get("assignmentRules", {})
        if not assignment_rules:
            return []

        return self.sort_assignment_rules(assignment_rules)

    def sort_assignment_rules(
        self, assignment_rules: Dict[str, Any]
    ) -> List[Tuple[str, sympy.Expr]]:
        """Sort assignment rules in topological order based on dependencies

        This ensures that variables are computed before they are used in other
        assignment rules. For example, VBlood must be computed before Art
        which depends on VBlood.

        Args:
            assignment_rules: Dictionary of assignment rule data

        Returns:
            List of (variable, expression) tuples in dependency order

        Raises:
            ValueError: If circular dependency detected
        """
        # Parse all expressions first
        parsed_rules = {}
        for rule_id, rule in assignment_rules.items():
            variable = rule.get("variable")
            math_expr = rule.get("math", "0")
            
            try:
                expr = self.parser.parse(math_expr)
                parsed_rules[variable] = expr
            except Exception as e:
                print(f"Warning: Failed to parse assignment rule for {variable}: {e}")
                # Use a default value if parsing fails
                parsed_rules[variable] = sympy.Float(0.0)

        # Build dependency graph
        dependencies = self._build_dependency_graph(parsed_rules)

        # Topological sort
        sorted_vars = self._topological_sort(dependencies)

        # Return in sorted order
        return [(var, parsed_rules[var]) for var in sorted_vars if var in parsed_rules]

    def _build_dependency_graph(
        self, parsed_rules: Dict[str, sympy.Expr]
    ) -> Dict[str, Set[str]]:
        """Build dependency graph from parsed assignment rules

        Args:
            parsed_rules: Dictionary mapping variable names to parsed expressions

        Returns:
            Dictionary mapping each variable to set of variables it depends on
        """
        dependencies = {}

        for variable, expr in parsed_rules.items():
            # Get all symbols in the expression
            symbols = expr.free_symbols
            
            # Find which symbols are also assignment rule variables
            deps = set()
            for sym in symbols:
                sym_name = str(sym)
                if sym_name in parsed_rules and sym_name != variable:
                    deps.add(sym_name)
            
            dependencies[variable] = deps

        return dependencies

    def _topological_sort(self, dependencies: Dict[str, Set[str]]) -> List[str]:
        """Perform topological sort on dependency graph using Kahn's algorithm

        Args:
            dependencies: Dictionary mapping variables to their dependencies

        Returns:
            List of variable names in topological order

        Raises:
            ValueError: If circular dependency is detected
        """
        # Calculate in-degree for each node
        # In-degree = number of dependencies that variable has
        in_degree = {var: len(deps) for var, deps in dependencies.items()}
        
        # Find all nodes with in-degree 0 (no dependencies)
        queue = [var for var, degree in in_degree.items() if degree == 0]
        sorted_vars = []

        while queue:
            # Remove a node from queue
            current = queue.pop(0)
            sorted_vars.append(current)

            # For each variable that depends on current, reduce its in-degree
            for var, deps in dependencies.items():
                if current in deps:
                    in_degree[var] -= 1
                    if in_degree[var] == 0:
                        queue.append(var)

        # Check if all nodes were processed (no cycles)
        if len(sorted_vars) != len(dependencies):
            unprocessed = set(dependencies.keys()) - set(sorted_vars)
            raise ValueError(
                f"Circular dependency detected in assignment rules: {unprocessed}"
            )

        return sorted_vars

    def get_assigned_variables(
        self, assignment_rules: Dict[str, Any]
    ) -> Set[str]:
        """Get set of all variables that are assigned by rules

        Args:
            assignment_rules: Dictionary of assignment rule data

        Returns:
            Set of variable names
        """
        return {
            rule.get("variable")
            for rule in assignment_rules.values()
            if rule.get("variable")
        }
