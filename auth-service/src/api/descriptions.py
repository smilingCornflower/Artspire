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
- **452 UsernameAlreadyExists**: If the username already in use.
- **453 EmailAlreadyExists**: If the email already in use.
- **455 Username Too Long**: If the username exceeds the allowed length (50).
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
description_profile: str = """
**Description**  
- Retrieves the profile information of a specified user by their username.
- If the authenticated user's username matches the specified username, a private view with more details is returned.
- Otherwise, a public view of the profile is returned.

**Request Query**  
- **username**: The username of the profile to retrieve.

**Request Header**  
- **Authorization**: Bearer token for authentication.

**Responses**  
- **227**: Successfully retrieved the private profile (for the authenticated user).
- **228**: Successfully retrieved the public profile (for other users).
- **404 Not Found**: If the specified username does not exist.
- **401 Unauthorized**: If the Bearer token is invalid, expired, or missing.
"""
description_post_subscribe = """
**Description**  
- Adds a subscription for the current user to follow a specific artist.
- Uses the current user's ID (retrieved from the access token) and the provided **artist_id** to create a new subscription.
- If the user is already subscribed to the artist, the request will have no effect, and the response will indicate that no new subscription was created.

**Request Body**  
- **artist_id**: ID of the artist user to subscribe to.

**Responses**  
- **200 OK**: Subscription successfully added or already exists. Returns *True* if a new subscription was created, *False* if the subscription already existed.
- **401 Unauthorized**: If the user is not authenticated or the access token is invalid.
- **404 Not Found**: If the artist with the provided ID does not exist.
"""
description_post_unsubscribe = """
**Description**  
- Removes an existing subscription for the current user to a specified artist.
- Uses the current user's ID (retrieved from the access token) and the provided **artist_id** to identify and delete the subscription record.
- If the user is not subscribed to the specified artist, the request will have no effect, and the response will indicate that no subscription was removed.

**Request Body**  
- **artist_id**: ID of the artist to unsubscribe from.

**Responses**  
- **200 OK**: Subscription successfully removed. Returns *True* if a subscription was deleted, *False* if no subscription existed.
- **401 Unauthorized**: If the user is not authenticated or the access token is invalid.
"""

description_change_username: str = """
**Description**  
- Changes the username of the currently authenticated user.  
- Requires a valid Bearer token for authentication.  
- Validates the new username to ensure it is unique and not excessively long.  
- If validation passes, updates the username and issues a new access token.

**Request Body**  
- **new_username**: The desired new username for the authenticated user.

**Responses**  
- **200 OK**: Successfully changed the username. Returns a new access token.  
- **452 Username Already Exists**: If the new username is already in use.  
- **455 Username Too Long**: If the new username exceeds the allowed length (50).  
- **401 Unauthorized**: If the Bearer token is invalid, expired, or missing.
"""
description_post_profile_picture: str = """
**Description**  
- Accepts an uploaded image file as the new profile picture for the authenticated user.

**Request Form**  
- **profile_picture**: The uploaded file (image) to set as the new profile picture.

**Request Header**  
- **Authorization**: Bearer token for authentication.

**Responses**  
- **201 Created**: Successfully updated the profile picture.
- **401 Unauthorized**: If the Bearer token is invalid, expired, or missing.
- **422 Unprocessable Entity**: If the uploaded file is invalid (not a jpg, png, webp).
"""
description_get_profile_picture: str = """
**Description**  
- Retrieves the URL of the user's profile picture by their user ID.

**Request Query**  
- **user_id**: The ID of the user whose profile picture is requested.

**Responses**  
- **200 OK**: Successfully returns the profile picture URL as a string.
- **401 Unauthorized**: If the request is made without proper authentication or an invalid token.
- **404 Not Found**: If the specified user does not exist in the database.
"""
