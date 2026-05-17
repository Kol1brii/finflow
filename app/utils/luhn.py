import random


def calculate_check_digit(digits: list[int]) -> int:
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 0:
            doubled = digit * 2
            total += (doubled - 9) if doubled > 9 else doubled
        else:
            total += digit

    return (10 - total % 10) % 10


def generate_luhn_number(length: int = 16) -> str:
    if length < 2:
        raise ValueError("Длина номера должна быть не менее 2 цифр")

    digits = [random.randint(0, 9) for _ in range(length - 1)]
    check_digit = calculate_check_digit(digits)
    digits.append(check_digit)

    return ''.join(map(str, digits))


def validate_luhn(number: str) -> bool:
    if not number.isdigit() or len(number) < 2:
        return False

    digits = [int(d) for d in number]
    check_digit = digits.pop()
    return calculate_check_digit(digits) == check_digit