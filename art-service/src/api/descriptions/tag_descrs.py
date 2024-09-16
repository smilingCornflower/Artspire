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
