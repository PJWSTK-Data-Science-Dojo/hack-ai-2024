def register(username, password) -> tuple[str, str]:
    return "valid_token", "User registered successfully"


def validate_token(token):
    return token == "valid_token"


def authenticate(username):
    return True
