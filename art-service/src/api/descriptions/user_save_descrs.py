description_get_user_saves: str = """
**Description**
- Retrieves a list of art saved by the user. Supports pagination and the option to include associated tags for each artwork.

**Parameters:**  
- **offset**: Optional integer. The number of items to skip before starting to return results.
- **limit**: Optional integer. The maximum number of items to return.
- **include_tags**: Optional boolean. If True, includes tags associated with each artwork in the response.

**Returns:**
- **200 OK**: Success, returns a list of saved art.
- **401 Unauthorized**: If the user is not authorized, you should provide jwt in headers to authorize
- **500 Internal Server Error**: If an unexpected server error occurs during the retrieval process.

**Authentication Required:**
- The user must be authenticated to make this request.
"""
description_post_user_save: str = """
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
description_delete_user_save: str = """
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
