description_get_arts: str = """
**Description:**  
- This endpoint retrieves information about art entities from the repository. 
- Depending on the provided **art_id** parameter, it can either return a specific art entity with the given ID or a list of all available art entities.

**Query Parameters:**  
- **art_id** (optional): The ID of the art entity to retrieve. If this parameter is not provided, all available art entities will be returned.

**Responses:**  
- **200 OK**: Successful request. Returns a list of art objects.
- **404 Not Found**: If no art entities are found for the provided **art_id**.
- **500 Internal Server Error**: If an unexpected server error occurs during processing.
"""

description_post_art: str = """
**Description:**
- Uploads a new art, storing its file and associated metadata.

**Parameters:**  
- **art_file**: The file of the art to be uploaded.
- **art_tags**: A comma-separated list of tags for the art.
- **art_title**: Optional title for the art. If not provided, the art will have no title.

**Returns:**
- **201 CREATED**: Successful, the ID of the newly created art entity.
- **422 Unprocessable Entity**: If server cannot process this type of file.
- **401 Unauthorized**: If the user is not authorized, you should provide jwt in headers to authorize
- **500 Internal Server Error**: If an unexpected server error occurs during processing.

**Authentication Required:**
- The user must be authenticated to make this request.
"""

description_delete_art: str = """
**Description**: Deletes an art by its ID.

**Parameters:**  
- **art_id**: The ID of the art to delete.  

**Returns:**  
- **200 OK**: True If the art was successfully deleted.  
- **200 OK**: False If the art was not found.  
- **401 Unauthorized**: If the user is not authorized, you should provide jwt in headers to authorize
- **403 Forbidden**: If the user lacks the necessary permissions to delete the art.  
- **500 Internal Server Error**: If an unexpected server error occurs during processing.

**Permission Required:**
- The ordinary user can delete only own art.
- To delete other's arts the user must be at least a moderator to make this request.
"""


description_get_tags: str = """
**Description**
- Retrieves a list of all tags in the system.

**Parameters:**  
- None

**Returns:**
- **200 OK**: Success, returns a list of tags.
- **500 Internal Server Error**: If an unexpected server error occurs during the retrieval process.
"""

description_post_tag: str = """
**Description**
- Adds a new tag to the system.

**Parameters:**  
- **tag_name**: The name of the tag to be added.

**Returns:**
- **201 CREATED**: Success, returns the ID of the newly created tag.
- **401 Unauthorized**: If the user is not authorized, you should provide jwt in headers to authorize
- **409 Conflict**: If the tag already exists.
- **500 Internal Server Error**: If an unexpected server error occurs during the creation process.

**Permission Required:**
- The user must be at least a moderator to make this request.
"""

description_delete_tag: str = """
**Description**: Deletes a tag by its ID.

**Parameters:**  
- **tag_id**: The ID of the tag to delete.  

**Returns:**  
- **200 OK**: True If the tag was successfully deleted.  
- **200 OK**: False If the tag was not found.
- **401 Unauthorized**: If the user is not authorized, you should provide jwt in headers to authorize  
- **500 Internal Server Error**: If an unexpected server error occurs during processing.

**Permission Required:**
- The user must be at least a moderator to make this request.
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