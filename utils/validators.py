# File: sbml_rust_generator/utils/validators.py
"""Utilities for validating and sanitizing identifiers"""

import re


class IdentifierValidator:
    """Validates and sanitizes identifiers for target languages"""

    @staticmethod
    def to_rust_identifier(name: str) -> str:
        """Convert a name to a valid Rust identifier

        Sanitizes names by:
        - Replacing non-alphanumeric characters with underscores
        - Prepending underscore if name starts with digit
        - Converting to lowercase

        Args:
            name: The original identifier name

        Returns:
            Valid Rust identifier string

        Examples:
            >>> IdentifierValidator.to_rust_identifier("Species-1")
            '_species_1'
            >>> IdentifierValidator.to_rust_identifier("k_cat")
            'k_cat'
        """
        clean = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if clean and clean[0].isdigit():
            clean = f"_{clean}"
        return clean.lower()

    @staticmethod
    def is_valid_rust_identifier(name: str) -> bool:
        """Check if a name is a valid Rust identifier

        Args:
            name: The identifier to validate

        Returns:
            True if valid Rust identifier, False otherwise
        """
        if not name:
            return False

        # Rust keywords that cannot be used as identifiers
        rust_keywords = {
            'as', 'break', 'const', 'continue', 'crate', 'else', 'enum',
            'extern', 'false', 'fn', 'for', 'if', 'impl', 'in', 'let',
            'loop', 'match', 'mod', 'move', 'mut', 'pub', 'ref', 'return',
            'self', 'Self', 'static', 'struct', 'super', 'trait', 'true',
            'type', 'unsafe', 'use', 'where', 'while', 'async', 'await', 'dyn'
        }

        # Check first character (must be letter or underscore)
        if not (name[0].isalpha() or name[0] == '_'):
            return False

        # Check remaining characters (alphanumeric or underscore)
        if not all(c.isalnum() or c == '_' for c in name):
            return False

        # Check if it's a reserved keyword
        if name in rust_keywords:
            return False

        return True
