from client import fetch_status


def ping(url: str) -> bool:
    return fetch_status(url) == 200
