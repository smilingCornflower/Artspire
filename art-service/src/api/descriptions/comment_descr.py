description_post_comment: str = """
**Description**
- Adds a new comment to a specified art.

**Parameters:**  
- **comment_create_data**: The data schema containing the comment text and the ID of the art.

**Returns:**
- **201 CREATED**: Success, returns the ID of the newly created comment.
- **400 Bad Request**: If the comment text is empty or exceeds the allowed length of 512 characters.
- **404 Not Found**: If the art with the specified ID is not found.
- **500 Internal Server Error**: If an unexpected server error occurs during the comment creation process.

**Permission Required:**
- The user must be authenticated to make this request.
"""
