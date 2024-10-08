description_register: str = """
**Description**  
- This endpoint registers a new user in the system. 
- It checks if the provided username or email is already in use and validates the password length. 
- If the username or email is taken, or if the password is too weak, appropriate errors are raised.

**Request Forms**  
- **username**: The username for the new user.
- **email**: The email address for the new user.
- **password**: The password for the new user, which must be at least 6 characters long.

**Responses**  
- **201 Created**: Successful registration. Returns the ID of the newly created user.
- **409 Conflict**: If the username or email is already in use.
- **400 Bad Request**: If the password is too weak.
- **422 Unprocessable Entity**: If an username or an email in wrong format.
"""

description_login: str = """
**Description**  
- Validates a user's credentials and generates an authentication token.
- Checks if the username exists and if the user is active. Validates the provided password.
- Raises an exception if the username does not exist, the user is inactive, or the password is incorrect. 
- If validation is successful, generates and returns an authentication token.

**Request Forms**  
- **username**: The username for authentication.
- **password**: The password for authentication.

**Responses**  
- **200 OK**: Successful authentication. Returns a list with two tokens: access and refresh tokens.
- **401 Unauthorized**: If the username does not exist, the user is not active, or the password is incorrect.
"""

description_refresh = """
**Description**  
- Refreshes the access token using the provided Bearer token from HTTP headers.
- Extracts the Bearer token from the *Authorization* header and verifies its validity.
- Generates a new access token while the refresh token is still valid. The refresh token remains unchanged.

**Request Header**  
- **Authorization**: Bearer <refresh token>.

**Responses**  
- **201 Created**: Successfully generated a new access token. Returns a *TokenInfoSchema* containing the new access token.
- **401 Unauthorized**: If the Bearer token is invalid, expired, or missing.
"""
description_me = """
**Description**  
- Retrieves and decodes the Bearer access token from the HTTP *Authorization* header.
- Validates the token and extracts the user information.
- Returns the user details in JSON format if the token is valid.

**Request Header**  
- **Authorization**: Bearer token for authentication.

**Responses**  
- **200 OK**: Successfully retrieves and decodes the token. Returns user information in the following JSON format:
- **401 Unauthorized**: If the Bearer token is invalid, expired, or missing.
"""
