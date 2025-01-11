description_get_arts: str = """
**Description:**  
- Retrieve art entities from the database, either as a specific art (if **art_id** is provided) or as a list of arts with optional pagination.  
- If the URL of any art entity is outdated, it will be refreshed automatically before returning the data.  
- Optionally includes the like status of arts for the authenticated user if a bearer token is provided.

**Parameters:**  
- **art_id** (optional): The ID of the art entity to retrieve. If not provided, a list of arts will be returned.  
- **offset** (optional): The number of arts to skip, for pagination.  
- **limit** (optional): The maximum number of arts to return.  
- **random_seed** (optional): A value in the range -1.0 ≤ x ≤ 1.0 to set the random seed for reproducibility. Raises a 400 status code if the input is outside this range.

**Returns:**  
- **200 OK**: Returns a list of art entities or a single art, including any refreshed URLs and optional like status (if authenticated).  
- **404 Not Found**: If no arts are found.  
- **400 Bad Request**: If the random_seed value is outside the allowed range (-1.0 to 1.0).  
- **500 Internal Server Error**: If there is an error during data retrieval or processing.

**Authentication and Permissions:**  
- A bearer token may be provided to retrieve the like status of the authenticated user. If no token is provided, the like status will not be included.
"""

description_post_art: str = """
**Description:**
- Upload a new art, storing its file and associated metadata such as title and tags.

**Parameters:**  
- **art_file**: The file representing the art to be uploaded.
- **art_tags**: A comma-separated list of tags to associate with the art.
- **art_title**: Optional title for the art. If not provided, the art will be created without a title.

**Returns:**  
- **201 CREATED**: Successfully created, returns the ID of the newly created art entity.
- **422 Unprocessable Entity**: If the server cannot process the provided file type.
- **401 Unauthorized**: If the user is not authenticated. Provide a valid JWT token in headers.
- **500 Internal Server Error**: If an unexpected server error occurs during processing.

**Authentication and Permissions:**  
- The user must be authenticated to perform this operation.
"""

description_delete_art: str = """
**Description:**  
- Delete an art by its ID.

**Parameters:**  
- **art_id**: The ID of the art to delete.

**Returns:**  
- **200 OK**: **True** if the art was successfully deleted.  
- **200 OK**: **False** if the art was not found.  
- **401 Unauthorized**: If the user is not authenticated. Provide a valid JWT token in headers.  
- **403 Forbidden**: If the user does not have permission to delete the art.  
- **500 Internal Server Error**: If an unexpected server error occurs during processing.

**Authentication and Permissions:**  
- A regular user can delete only their own art.
- A moderator or higher permissions are required to delete others' art.
"""

description_get_similar_arts: str = """
**Description:**  
- Retrieve a list of arts similar to a specified art ID using the similarity algorithm.  
- If the specified **art_id** is not found in the database, random arts will be selected instead, without applying any similarity algorithms.  
- The like status of the arts is included for the authenticated user if a bearer token is provided. If no token is provided, the like status will always be **False**.

**Parameters:**  
- **art_id** (required): The ID of the art for which similar arts are being retrieved.  
- **offset** (optional): The number of similar arts to skip.  
- **limit** (optional): The maximum number of similar arts to return.  

**Returns:**  
- **200 OK**: Returns a list of arts similar to the specified art ID, or random arts if **art_id** is not found.  
- **500 Internal Server Error**: If there is an error during data retrieval or processing.

**Authentication and Permissions:**  
- A bearer token may be provided to retrieve the like status of the authenticated user. If no token is provided, the like status will always be **False**.
"""
