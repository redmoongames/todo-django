import re
from typing import Tuple, List


MIN_LENGTH = 8
UPPERCASE_PATTERN = r"[A-Z]"
LOWERCASE_PATTERN = r"[a-z]"
NUMBER_PATTERN = r"\d"
SPECIAL_CHAR_PATTERN = r"[!@#$%^&*]"

def validate_password(password: str) -> Tuple[bool, List[str]]:
    """
    Validate the password based on the following criteria:
    - Minimum length of 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character (!@#$%^&*)
    """
    errors: List[str] = []
    
    if len(password) < MIN_LENGTH:
        errors.append(f"Password must be at least {MIN_LENGTH} characters long.")

    if not _contains_pattern(password, UPPERCASE_PATTERN):
        errors.append("Password must contain at least one uppercase letter.")

    if not _contains_pattern(password, LOWERCASE_PATTERN):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not _contains_pattern(password, NUMBER_PATTERN):
        errors.append("Password must contain at least one number.")
    
    if not _contains_pattern(password, SPECIAL_CHAR_PATTERN):
        errors.append("Password must contain at least one special character (!@#$%^&*).")

    return len(errors) == 0, errors

def _contains_pattern(text: str, pattern: str) -> bool:
    return re.search(pattern, text) is not None
