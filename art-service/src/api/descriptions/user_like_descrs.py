description_post_user_like: str = """
**Description**: Add an art to the user's saved list.

**Parameters:**  
- **art_id**: The ID of the art to be saved.

**Returns:**  
- **201 CREATED**: True if record has written, False if such pair already exists in repository
- **401 Unauthorized**: If the user is not authorized, you should provide jwt in headers to authorize
- **404 Not Found**: If the art with the given **art_id** is not found.
- **500 Internal Server Error**: If there is a database error during the operation.

**Permission Required:**  
- User must be authenticated.
"""


description_delete_user_like: str = """
**Description**: Deletes the user save by art_id

**Parameters:**  
- **art_id**: The ID of the saved art to delete.  

**Returns:**  
- **200 OK**: True If the art was successfully removed from saved list.  
- **200 OK**: False If the art with this id was not found.  
- **401 Unauthorized**: If the user is not authorized, you should provide jwt in headers to authorize
- **500 Internal Server Error**: If an unexpected server error occurs during processing.

**Permission Required:**
- User must be authenticated.
"""
