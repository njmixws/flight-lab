"""Running queries against the flight database."""
from validator import parse_datetime

RECORD_KEYS = ("flight_id", "origin", "destination",
               "departure_datetime", "arrival_datetime", "price")
_STRING_KEYS = {"flight_id", "origin", "destination"}
_DATETIME_KEYS = {"departure_datetime", "arrival_datetime"}
_NUMBER_KEYS = {"price", "min_price"}
_ALLOWED_KEYS = (_STRING_KEYS | _DATETIME_KEYS | _NUMBER_KEYS
                 | {"sort_by", "order", "limit"})


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_valid(query) -> bool:
    if not isinstance(query, dict):
        return False
    for key, value in query.items():
        if key not in _ALLOWED_KEYS:
            return False
        if key in _STRING_KEYS:
            if not isinstance(value, str):
                return False
        elif key in _DATETIME_KEYS:
            if parse_datetime(value) is None:
                return False
        elif key in _NUMBER_KEYS:
            if not _is_number(value):
                return False
        elif key == "sort_by":
            if not isinstance(value, str) or value not in RECORD_KEYS:
                return False
        elif key == "order":
            if not isinstance(value, str) or value not in ("asc", "desc"):
                return False
        elif key == "limit":
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return False
    if "order" in query and "sort_by" not in query:
        return False
    return True


def _matches(flight: dict, q: dict) -> bool:
    for key in _STRING_KEYS:
        if key in q and flight.get(key) != q[key]:
            return False
    # 'YYYY-MM-DD HH:MM' strings sort chronologically.
    if "departure_datetime" in q and not flight["departure_datetime"] >= q["departure_datetime"]:
        return False
    if "arrival_datetime" in q and not flight["arrival_datetime"] <= q["arrival_datetime"]:
        return False
    if "price" in q and not flight["price"] <= q["price"]:
        return False
    if "min_price" in q and not flight["price"] >= q["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not _is_valid(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
    matches = [flight for flight in db if _matches(flight, query)]
    if "sort_by" in query:
        # sorted() is stable, also with reverse=True.
        matches = sorted(matches, key=lambda r: r[query["sort_by"]],
                         reverse=query.get("order", "asc") == "desc")
    if "limit" in query:
        matches = matches[:query["limit"]]
    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if not isinstance(queries, list):
        queries = [queries]
    return [run_query(db, q) for q in queries]
