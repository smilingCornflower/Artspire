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

description_get_comments: str = """
**Description**: Retrieves a list of comments for a specific art.

**Parameters:**  
- **art_id**: The ID of the art for which comments are being retrieved.  
- **offset** (optional): The number of comments to skip before starting to collect the result set.
- **limit** (optional): The maximum number of comments to return in the response.

**Returns:**  
- **200 OK**: A list of comments(dict) with detailed information:
- **200 OK**: An empty list if no comments are found for the given **art_id**.  
- **500 Internal Server Error**: If there is a database error during comment retrieval.

**Permission Required:**
- None (public access).
"""
