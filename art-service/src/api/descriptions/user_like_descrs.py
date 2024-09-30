description_post_user_like: str = """
**Description**
- Allows the user to like a specific art. The like is associated with the user and the art, and the system ensures that the same user cannot like the same art more than once.

**Parameters:**  
- **art_id**: The ID of the art to be liked.  

**Returns:**
- **200 OK**: 
    - True if the like was successfully added.
    - False if the user has already liked the art (i.e., the like was not added because it already exists).
- **404 Not Found**: If the art with the provided **art_id** does not exist.
- **500 Internal Server Error**: If an unexpected error occurs during the process.

**Authentication Required:**
- The user must be authenticated to like an art.
"""

description_delete_user_like: str = """
**Description**
- Allows the user to remove their like from a specific art. The like is disassociated from the user and the art, and the like counter for the art is decreased.

**Parameters:**  
- **art_id**: The ID of the art from which to remove the like.

**Returns:**
- **200 OK**: 
    - True if the like was successfully removed.
    - False if no like existed for the provided **art_id**
- **500 Internal Server Error**: If an unexpected error occurs during the process.

**Authentication Required:**
- The user must be authenticated to remove a like from an art.
"""
