"""
Supabase REST client via httpx — sem dependência do supabase-py.
Implementa apenas o subconjunto necessário: select, insert, update, eq, order, limit, in_.
"""
import httpx
from app.config import get_settings
from functools import lru_cache
from typing import Any


class QueryBuilder:
    def __init__(self, client: "SupabaseClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[str] = []
        self._order_col: str | None = None
        self._order_desc = False
        self._limit_val: int | None = None
        self._single = False
        self._method = "GET"
        self._body: dict | list | None = None

    def select(self, cols: str = "*"):
        self._select = cols
        return self

    def eq(self, col: str, val: Any):
        self._filters.append(f"{col}=eq.{val}")
        return self

    def in_(self, col: str, vals: list):
        joined = ",".join(str(v) for v in vals)
        self._filters.append(f"{col}=in.({joined})")
        return self

    def gte(self, col: str, val: Any):
        self._filters.append(f"{col}=gte.{val}")
        return self

    def lte(self, col: str, val: Any):
        self._filters.append(f"{col}=lte.{val}")
        return self

    def order(self, col: str, desc: bool = False, ascending: bool = True):
        self._order_col = col
        self._order_desc = desc or not ascending
        return self

    def limit(self, n: int):
        self._limit_val = n
        return self

    def single(self):
        self._single = True
        return self

    def insert(self, data: dict | list):
        self._method = "POST"
        self._body = data
        return self

    def update(self, data: dict):
        self._method = "PATCH"
        self._body = data
        return self

    def _build_url(self) -> str:
        params: list[str] = [f"select={self._select}"]
        params.extend(self._filters)
        if self._order_col:
            direction = "desc" if self._order_desc else "asc"
            params.append(f"order={self._order_col}.{direction}")
        if self._limit_val is not None:
            params.append(f"limit={self._limit_val}")
        qs = "&".join(params)
        return f"{self._client.base_url}/{self._table}?{qs}"

    def execute(self) -> "Result":
        url = self._build_url()
        headers = dict(self._client.headers)
        if self._single:
            headers["Accept"] = "application/vnd.pgrst.object+json"
        if self._method in ("POST", "PATCH"):
            headers["Prefer"] = "return=representation"

        with httpx.Client(timeout=20) as client:
            if self._method == "GET":
                resp = client.get(url, headers=headers)
            elif self._method == "POST":
                resp = client.post(url, headers=headers, json=self._body)
            elif self._method == "PATCH":
                resp = client.patch(url, headers=headers, json=self._body)
            else:
                resp = client.request(self._method, url, headers=headers, json=self._body)

        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            data = [data] if data else []
        return Result(data)


class RpcBuilder:
    def __init__(self, client: "SupabaseClient", fn: str, params: dict):
        self._client = client
        self._fn = fn
        self._params = params

    def execute(self) -> "Result":
        url = f"{self._client.base_url}/rpc/{self._fn}"
        with httpx.Client(timeout=20) as client:
            resp = client.post(url, headers=self._client.headers, json=self._params)
        resp.raise_for_status()
        data = resp.json()
        return Result(data if isinstance(data, list) else [data])


class Result:
    def __init__(self, data: list):
        self.data = data


class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.base_url = f"{url}/rest/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def table(self, name: str) -> QueryBuilder:
        return QueryBuilder(self, name)

    def rpc(self, fn: str, params: dict) -> RpcBuilder:
        return RpcBuilder(self, fn, params)


@lru_cache
def get_db() -> SupabaseClient:
    s = get_settings()
    return SupabaseClient(s.supabase_url, s.supabase_service_key)
