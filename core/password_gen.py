import secrets
import string

def generate_strong_password(length=16):
    # 1. Define the character pools
    letters = string.ascii_letters
    digits = string.digits
    symbols = string.punctuation
    all_characters = letters + digits + symbols

    # 2. Guarantee at least one number and one symbol
    guaranteed_digit = secrets.choice(digits)
    guaranteed_symbol = secrets.choice(symbols)

    # 3. Fill the rest of the password length with random characters
    remaining_length = length - 2
    rest_of_password = [secrets.choice(all_characters) for _ in range(remaining_length)]

    # 4. Combine them all into a list
    password_list = [guaranteed_digit, guaranteed_symbol] + rest_of_password

    # 5. Shuffle the list securely so the guaranteed characters aren't always first
    secrets.SystemRandom().shuffle(password_list)

    # 6. Join the list back into a single string
    final_password = "".join(password_list)
    
    return final_password

# Test Block - This only runs if you run this file directly
if __name__ == "__main__":
    print("Testing Secure Password Generator:")
    print("Password 1 (16 chars):", generate_strong_password(16))
    print("Password 2 (20 chars):", generate_strong_password(20))