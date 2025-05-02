from enum import Enum

class OTPEnum(str, Enum):  # str mixin is good for comparison
    REGISTER = "REGISTER"
    FORGOT = "FORGOT"