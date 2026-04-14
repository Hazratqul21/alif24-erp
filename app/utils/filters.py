from sqlalchemy import Column, String, Integer, Date, Boolean, and_
from sqlalchemy.sql import Select
from typing import Any, Optional
from datetime import date


def apply_filters(query: Select, model: Any, filters: dict) -> Select:
    conditions = []
    for field_name, value in filters.items():
        if value is None:
            continue
        column = getattr(model, field_name, None)
        if column is None:
            continue

        col_type = getattr(column.type, "__class__", None)

        if isinstance(value, str) and col_type in (String,):
            conditions.append(column.ilike(f"%{value}%"))
        elif isinstance(value, dict):
            if "gte" in value and value["gte"] is not None:
                conditions.append(column >= value["gte"])
            if "lte" in value and value["lte"] is not None:
                conditions.append(column <= value["lte"])
            if "eq" in value and value["eq"] is not None:
                conditions.append(column == value["eq"])
        else:
            conditions.append(column == value)

    if conditions:
        query = query.where(and_(*conditions))
    return query


def apply_sorting(query: Select, model: Any, sort_by: Optional[str], sort_order: str = "asc") -> Select:
    if not sort_by:
        return query
    column = getattr(model, sort_by, None)
    if column is None:
        return query
    if sort_order.lower() == "desc":
        return query.order_by(column.desc())
    return query.order_by(column.asc())
