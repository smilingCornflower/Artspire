description_get_arts: str = """
**Description:**  
- This endpoint retrieves information about art entities from the repository. 
- Depending on the provided **art_id** parameter, it can either return a specific art entity with the given ID or a list of all available art entities.

**Json Parameters:**  
- **art_id** (optional): The ID of the art entity to retrieve. If this parameter is not provided, all available art entities will be returned.            
- **param offset** (optional): The number of arts to skip, for pagination.
- **param limit** (optional): The maximum number of arts to return.

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
