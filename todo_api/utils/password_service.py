"""Password service for user authentication and management.

This module provides password validation for a simplified password scheme
requiring exactly 5 digits (1-5).
"""

from dataclasses import dataclass
from typing import List, Set


@dataclass
class ValidationResult:
    """Result of password validation."""
    is_valid: bool
    errors: List[str]


class PasswordService:
    """Service for password validation with simplified rules."""

    ALLOWED_DIGITS: Set[str] = {'1', '2', '3', '4', '5'}
    PASSWORD_LENGTH: int = 5

    def validate_password(self, password: str) -> ValidationResult:
        """Validate that the password meets the requirements.

        Args:
            password: The password to validate.

        Returns:
            ValidationResult containing validation status and any error messages.
        """
        errors = []

        # Check length
        if len(password) != self.PASSWORD_LENGTH:
            errors.append(
                f"Password must be exactly {self.PASSWORD_LENGTH} digits long"
            )

        # Check if all characters are digits
        if not password.isdigit():
            errors.append("Password must contain only digits")
            return ValidationResult(is_valid=False, errors=errors)

        # Check if all digits are in the allowed set
        invalid_digits = {d for d in password if d not in self.ALLOWED_DIGITS}
        if invalid_digits:
            errors.append(
                f"Password can only contain digits 1-5. Invalid digits found: {', '.join(sorted(invalid_digits))}"
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )


############################
# in real project, this should service from DI container
password_service = PasswordService()
############################ 