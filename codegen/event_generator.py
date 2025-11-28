# File: sbml_rust_generator/codegen/event_generator.py
"""Generates Rust code for SBML events using diffsol root finding"""

from typing import Dict, List, Any


class EventCodeGenerator:
    """Generates Rust code for handling SBML events"""
    
    def __init__(self, code_generator, expression_parser):
        """Initialize with code generator and expression parser
        
        Args:
            code_generator: RustBlockGenerator instance for expression generation
            expression_parser: SbmlExpressionParser for parsing MathML
        """
        self.code_gen = code_generator
        self.expression_parser = expression_parser
    
    def generate_event_handling(
        self,
        events: Dict[str, Any],
        species_map: Dict[str, int]
    ) -> Dict[str, str]:
        """Generate comprehensive event handling code
        
        Args:
            events: Dictionary of event data from SBML
            species_map: Mapping of species IDs to indices
            
        Returns:
            Dictionary with keys: root_fn, event_handling, root_registration
        """
        if not events:
            return {}
        
        # Generate root function for triggers
        root_fn = self._generate_root_function(events)
        
        # Generate event handling in main loop  
        event_handling = self._generate_event_callback(events, species_map)
        
        # Generate root registration for OdeBuilder
        root_registration = f".root({len(events)}, root_fn)"
        
        return {
            "root_fn": root_fn,
            "event_handling": event_handling,
            "root_registration": root_registration
        }
    
    def _generate_root_function(self, events: Dict[str, Any]) -> str:
        """Generate root function for event triggers
        
        Args:
            events: Dictionary of event data
            
        Returns:
            Rust code for root function
        """
        code = "    let root_fn = |y: &diffsol::NalgebraVec<f64>, _p: &diffsol::NalgebraVec<f64>, t: f64, roots: &mut diffsol::NalgebraVec<f64>| {\n"
        
        for idx, (event_id, event_data) in enumerate(events.items()):
            trigger = event_data.get("trigger")
            if not trigger:
                # No trigger - shouldn't happen in valid SBML
                code += f"        roots[{idx}] = 1.0; // Event {event_id}: no trigger\n"
                continue
            
            try:
                # Parse trigger MathML to SymPy
                trigger_expr = self.expression_parser.parse(trigger)
                
                # Generate Rust code
                # For boolean expressions like "t > 5.0", we need to convert to root form
                # Root finding detects sign changes, so we use: trigger - 0.5
                # This means: when trigger goes from false (0) to true (1), root crosses zero
                trigger_rust = self.code_gen.generate(trigger_expr)
                
                code += f"        // Event {event_id}: trigger\n"
                code += f"        roots[{idx}] = ({trigger_rust}) as i32 as f64 - 0.5;\n"
                
            except Exception as e:
                print(f"Warning: Could not parse trigger for event {event_id}: {e}")
                code += f"        roots[{idx}] = 1.0; // {event_id}: parse error\n"
        
        code += "    };\n\n"
        return code
    
    def _generate_event_callback(
        self,
        events: Dict[str, Any],
        species_map: Dict[str, int]
    ) -> str:
        """Generate event handling code for main solver loop
        
        Args:
            events: Dictionary of event data
            species_map: Mapping of species IDs to indices
            
        Returns:
            Rust code for event handling in match statement
        """
        code = "            Ok(OdeSolverStopReason::RootFound(root_idx)) => {\n"
        code += "                console_log!(\"Event triggered at t={}\", solver.state().t);\n"
        code += "                match root_idx {\n"
        
        for idx, (event_id, event_data) in enumerate(events.items()):
            code += f"                    {idx} => {{\n"
            code += f"                        // Event: {event_id}\n"
            
            # Get event assignments
            assignments = event_data.get("eventAssignments", [])
            
            for assignment in assignments:
                variable = assignment.get("variable")
                math_ml = assignment.get("math")
                
                if not variable or not math_ml:
                    continue
                
                try:
                    # Parse assignment MathML
                    expr = self.expression_parser.parse(math_ml)
                    rust_expr = self.code_gen.generate(expr)
                    
                    # Determine if variable is a species or parameter
                    if variable in species_map:
                        idx_var = species_map[variable]
                        code += f"                        solver.state_mut().y[{idx_var}] = {rust_expr};\n"
                        code += f"                        console_log!(\"  {variable} = {{}}\", {rust_expr});\n"
                    else:
                        # It's a parameter - we can't modify parameters during simulation
                        # This is a limitation, but valid in SBML
                        code += f"                        // WARNING: Cannot modify parameter {variable} during simulation\n"
                        code += f"                        console_log!(\"  Skipping parameter assignment: {variable}\");\n"
                    
                except Exception as e:
                    print(f"Warning: Could not parse assignment for {variable}: {e}")
                    code += f"                        // Parse error for {variable}\n"
            
            code += "                    },\n"
        
        code += "                    _ => console_log!(\"Unknown event index: {}\", root_idx),\n"
        code += "                }\n"
        code += "            },\n"
        
        return code
    
    def will_implement_full_events(self):
        """Placeholder for full event implementation
        
        Full implementation would need:
        1. Root finding for event triggers ✅ IMPLEMENTED
        2. Event queue management  
        3. State updates from event assignments ✅ IMPLEMENTED
        4. Delay handling ⚠️  TODO
        5. Integration with diffsol solver callbacks ✅ IMPLEMENTED
        """
        pass
