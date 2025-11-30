import sympy
from typing import List, Tuple, Set, Dict, Any

class DependencyAnalyzer:
    """Analyzes dependencies of assignment rules to separate static (parameter-only) 
    from dynamic (species-dependent) rules."""
    
    def __init__(self, species_ids: List[str], param_ids: List[str]):
        self.species_ids = set(species_ids)
        self.param_ids = set(param_ids)
        
    def classify_rules(self, rules: List[Tuple[str, sympy.Expr]], external_dynamic_vars: Set[str] = None) -> Tuple[List[Tuple[str, sympy.Expr]], List[Tuple[str, sympy.Expr]]]:
        """
        Classify rules into static and dynamic, with static rules topologically sorted.
        
        Args:
            rules: List of (variable_id, expression) tuples
            external_dynamic_vars: Set of variable names that are known to be dynamic (e.g., dynamic initial assignments)
            
        Returns:
            (static_rules, dynamic_rules)
            - static_rules: Depend only on parameters and other static rules (topologically sorted)
            - dynamic_rules: Depend on species or time
        """
        if external_dynamic_vars is None:
            external_dynamic_vars = set()
        
        # Build a map of all rules for lookup
        rule_map = {var: expr for var, expr in rules}
        
        # Track which variables are known to be static or dynamic
        static_vars = self.param_ids.copy()
        dynamic_vars = self.species_ids.copy()
        dynamic_vars.add('t')
        dynamic_vars.add('time')
        # Add external dynamic variables
        dynamic_vars.update(external_dynamic_vars)
        
        # Multi-pass classification: keep iterating until no changes
        max_iterations = len(rules) + 1
        iteration = 0
        classified = set()
        static_list = []
        dynamic_list = []
        
        while iteration < max_iterations and len(classified) < len(rules):
            iteration += 1
            made_progress = False
            
            for var, expr in rules:
                if var in classified:
                    continue
                
                # Get all symbols in expression
                symbols = {str(s) for s in expr.free_symbols}
                
                # Check if depends on any known dynamic variable
                is_dynamic = False
                depends_on_unclassified = False
                
                for sym in symbols:
                    if sym in dynamic_vars:
                        is_dynamic = True
                        break
                    if sym in rule_map and sym not in classified:
                        # Depends on unclassified rule - can't classify yet
                        depends_on_unclassified = True
                        break
                    if sym not in rule_map and sym not in static_vars:
                        # Depends on something not in rules AND not in static_vars (e.g. an assignment rule)
                        # Treat as dynamic (deferred)
                        is_dynamic = True
                        break
                
                if is_dynamic:
                    # Mark as dynamic
                    dynamic_list.append((var, expr))
                    dynamic_vars.add(var)
                    classified.add(var)
                    made_progress = True
                elif not depends_on_unclassified:
                    # All dependencies are static - mark as static
                    static_list.append((var, expr))
                    static_vars.add(var)
                    classified.add(var)
                    made_progress = True
            
            if not made_progress and len(classified) < len(rules):
                # Circular dependency or can't classify - treat remaining as dynamic
                for var, expr in rules:
                    if var not in classified:
                        dynamic_list.append((var, expr))
                        classified.add(var)
                break
        
        # Topologically sort static rules
        dependencies = {}
        for var, expr in static_list:
            symbols = {str(s) for s in expr.free_symbols}
            deps = set()
            for sym in symbols:
                if sym in rule_map and sym in static_vars:
                    deps.add(sym)
            dependencies[var] = deps
        
        sorted_static = self._topological_sort(static_list, dependencies)
        
        return sorted_static, dynamic_list

    def _topological_sort(self, rules: List[Tuple[str, sympy.Expr]], dependencies: Dict[str, Set[str]]) -> List[Tuple[str, sympy.Expr]]:
        """
        Topologically sort rules based on dependencies.
        
        Args:
            rules: List of (var, expr) tuples
            dependencies: Dict mapping var -> set of vars it depends on
            
        Returns:
            Sorted list of rules where dependencies come before dependents
        """
        # Create a mapping from var to (var, expr)
        rule_map = {var: (var, expr) for var, expr in rules}
        
        # Track which variables are already defined (parameters)
        defined = self.param_ids.copy()
        
        sorted_rules = []
        remaining = set(rule_map.keys())
        
        # Iteratively add rules whose dependencies are all defined
        max_iterations = len(rules) + 1
        iteration = 0
        
        while remaining and iteration < max_iterations:
            iteration += 1
            made_progress = False
            
            # Find rules that can be added (all dependencies defined)
            ready = []
            for var in list(remaining):
                deps = dependencies.get(var, set())
                if deps.issubset(defined):
                    ready.append(var)
            
            # Add ready rules and mark as defined
            for var in ready:
                sorted_rules.append(rule_map[var])
                defined.add(var)
                remaining.remove(var)
                made_progress = True
            
            if not made_progress:
                # Circular dependency or unresolved dependency
                # Add remaining rules in original order as fallback
                for var in remaining:
                    sorted_rules.append(rule_map[var])
                break
        
        return sorted_rules
