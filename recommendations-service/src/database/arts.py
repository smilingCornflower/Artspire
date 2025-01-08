import numpy as np

from sqlalchemy import text as sql_text
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from datetime import datetime
from config import logger, settings

from .db import db_manager

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import TextClause, Result


class ArtsService:
    @staticmethod
    async def get_new_arts_data(start_date: datetime = None) -> list[list]:
        """
        Fetches art data from the database, starting from the specified date, and converts it into a feature matrix.

        Args:
            start_date (datetime, optional): The starting date for fetching data. If not provided, defaults to the earliest possible date (datetime.min).

        Returns:
            list[list]: A 2D list where:
                - Each inner list represents an individual art record.
                - The structure of each row is as follows:
                    1. id (int): The ID of the art.
                    2. user_id (int): The ID of the user associated with the art.
                    3. likes_count (int): The number of likes the art has received.
                    4. views_count (int): The number of views the art has received.
                    5. tags (list[int]): A list of tag IDs associated with the art.

        Matrix format:
            Each row contains:
                [id, user_id, likes_count, views_count, [tag1, tag2, ..., tagN]]
            where `tags` is a list of integers.

        Example:
            For the following database records:
                id | user_id | likes_count | views_count | tags
                1  | 101     | 10          | 200         | [1, 2, 4]
                2  | 102     | 15          | 250         | [3, 7]
            The resulting matrix would be:
                [
                    [1, 101, 10, 200, [1, 2, 4]],
                    [2, 102, 15, 250, [3, 7]]
                ]
        """
        logger.info(f"STARTED start_date={start_date}")
        if start_date is None:
            start_date: datetime = datetime.min
        stmt: "TextClause" = sql_text("""
                SELECT arts.id, arts.user_id, arts.likes_count, arts.views_count, array_agg(arts_to_tags.tag_id) as tags
                FROM arts
                JOIN arts_to_tags
                ON arts.id = arts_to_tags.art_id
                WHERE created_at >= :start_date
                GROUP BY arts.id, arts.user_id, arts.likes_count, arts.views_count;
                """)
        async with db_manager.async_session_maker() as session:
            sql_result: "Result" = await session.execute(stmt, {"start_date": start_date})
        logger.debug(f"SQL query executed")

        matrix: list = list()
        for r in sql_result.mappings():
            row = [r["id"], r["user_id"], r["likes_count"], r["views_count"], r["tags"]]
            matrix.append(row)
        return matrix

    @staticmethod
    async def get_all_tags() -> list[tuple[int, str]]:
        stmt: "TextClause" = sql_text("""SELECT id, name FROM tags;""")
        async with db_manager.async_session_maker() as session:
            sql_result: "Result" = await session.execute(stmt)
        tags: list[tuple[int, str]] = [(i["id"], i["name"]) for i in sql_result.mappings()]

        return tags
