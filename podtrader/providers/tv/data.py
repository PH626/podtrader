import datetime
import json
import random
import re
import string
from vectorbt.data.base import Data

import pandas as pd
import requests
from websocket import WebSocket
from vectorbt import _typing as tp
from vectorbt.utils.config import Configured

__all__ = [
    "TVClient",
]

SIGNIN_URL = "https://www.tradingview.com/accounts/signin/"
"""Sign-in URL."""

SEARCH_URL = (
    "https://symbol-search.tradingview.com/symbol_search/v3/?"
    "text={text}&"
    "start={start}&"
    "hl=1&"
    "exchange={exchange}&"
    "lang=en&"
    "search_type=undefined&"
    "domain=production&"
    "sort_by_country=US"
)
"""Symbol search URL."""

SCAN_URL = "https://scanner.tradingview.com/{market}/scan"
"""Market scanner URL."""

ORIGIN_URL = "https://data.tradingview.com"
"""Origin URL."""

REFERER_URL = "https://www.tradingview.com"
"""Referer URL."""

WS_URL = "wss://data.tradingview.com/socket.io/websocket"
"""Websocket URL."""

PRO_WS_URL = "wss://prodata.tradingview.com/socket.io/websocket"
"""Websocket URL (Pro)."""

WS_TIMEOUT = 5
"""Websocket timeout."""

MARKET_LIST = [
    "america",
    "argentina",
    "australia",
    "austria",
    "bahrain",
    "bangladesh",
    "belgium",
    "brazil",
    "canada",
    "chile",
    "china",
    "colombia",
    "cyprus",
    "czech",
    "denmark",
    "egypt",
    "estonia",
    "euronext",
    "finland",
    "france",
    "germany",
    "greece",
    "hongkong",
    "hungary",
    "iceland",
    "india",
    "indonesia",
    "israel",
    "italy",
    "japan",
    "kenya",
    "korea",
    "ksa",
    "kuwait",
    "latvia",
    "lithuania",
    "luxembourg",
    "malaysia",
    "mexico",
    "morocco",
    "netherlands",
    "newzealand",
    "nigeria",
    "norway",
    "pakistan",
    "peru",
    "philippines",
    "poland",
    "portugal",
    "qatar",
    "romania",
    "rsa",
    "russia",
    "serbia",
    "singapore",
    "slovakia",
    "spain",
    "srilanka",
    "sweden",
    "switzerland",
    "taiwan",
    "thailand",
    "tunisia",
    "turkey",
    "uae",
    "uk",
    "venezuela",
    "vietnam",
]
"""List of markets supported by the market scanner (list may be incomplete)."""

FIELD_LIST = [
    "name",
    "description",
    "logoid",
    "update_mode",
    "type",
    "typespecs",
    "close",
    "pricescale",
    "minmov",
    "fractional",
    "minmove2",
    "currency",
    "change",
    "change_abs",
    "Recommend.All",
    "volume",
    "Value.Traded",
    "market_cap_basic",
    "fundamental_currency_code",
    "Perf.1Y.MarketCap",
    "price_earnings_ttm",
    "earnings_per_share_basic_ttm",
    "number_of_employees_fy",
    "sector",
    "market",
]
"""List of fields supported by the market scanner (list may be incomplete)."""

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
"""User agent."""


class TVClient(Configured):
    """Client for TradingView."""

    def __init__(
        self,
        username: tp.Optional[str] = None,
        password: tp.Optional[str] = None,
        auth_token: tp.Optional[str] = None,
        **kwargs,
    ) -> None:
        """Client for TradingView."""
        Configured.__init__(
            self,
            username=username,
            password=password,
            auth_token=auth_token,
            **kwargs,
        )

        if auth_token is None:
            auth_token = self.auth(username, password)
        elif username is not None or password is not None:
            raise ValueError("Must provide either username and password, or auth_token")

        self._auth_token = auth_token
        self._ws = None
        self._session = self.generate_session()
        self._chart_session = self.generate_chart_session()

    @property
    def auth_token(self) -> str:
        """Authentication token."""
        return self._auth_token

    @property
    def ws(self) -> WebSocket:
        """Instance of `websocket.Websocket`."""
        return self._ws

    @property
    def session(self) -> str:
        """Session."""
        return self._session

    @property
    def chart_session(self) -> str:
        """Chart session."""
        return self._chart_session

    @classmethod
    def auth(
        cls,
        username: tp.Optional[str] = None,
        password: tp.Optional[str] = None,
    ) -> str:
        """Authenticate."""
        if username is not None and password is not None:
            data = {"username": username, "password": password, "remember": "on"}
            headers = {"Referer": REFERER_URL, "User-Agent": USER_AGENT}
            response = requests.post(url=SIGNIN_URL, data=data, headers=headers)
            response.raise_for_status()
            json = response.json()
            if "user" not in json or "auth_token" not in json["user"]:
                raise ValueError(json)
            return json["user"]["auth_token"]
        if username is not None or password is not None:
            raise ValueError("Must provide both username and password")
        return "unauthorized_user_token"

    @classmethod
    def generate_session(cls) -> str:
        """Generate session."""
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for _ in range(stringLength))
        return "qs_" + random_string

    @classmethod
    def generate_chart_session(cls) -> str:
        """Generate chart session."""
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for _ in range(stringLength))
        return "cs_" + random_string

    def create_connection(self, pro_data: bool = True) -> None:
        """Create a websocket connection."""
        from websocket import create_connection

        if pro_data:
            self._ws = create_connection(
                PRO_WS_URL,
                headers=json.dumps({"Origin": ORIGIN_URL}),
                timeout=WS_TIMEOUT,
            )
        else:
            self._ws = create_connection(
                WS_URL,
                headers=json.dumps({"Origin": ORIGIN_URL}),
                timeout=WS_TIMEOUT,
            )

    @classmethod
    def filter_raw_message(cls, text) -> tp.Tuple[str, str]:
        """Filter raw message."""
        found = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
        return found, found2

    @classmethod
    def prepend_header(cls, st: str) -> str:
        """Prepend a header."""
        return "~m~" + str(len(st)) + "~m~" + st

    @classmethod
    def construct_message(cls, func: str, param_list: tp.List[str]) -> str:
        """Construct a message."""
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def create_message(self, func: str, param_list: tp.List[str]) -> str:
        """Create a message."""
        return self.prepend_header(self.construct_message(func, param_list))

    def send_message(self, func: str, param_list: tp.List[str]) -> None:
        """Send a message."""
        m = self.create_message(func, param_list)
        self.ws.send(m)

    @classmethod
    def convert_raw_data(cls, raw_data: str, symbol: str) -> pd.DataFrame:
        """Process raw data into a DataFrame."""
        search_result = re.search(r'"s":\[(.+?)\}\]', raw_data)
        if search_result is None:
            raise ValueError("Couldn't parse data returned by TradingView: {}".format(raw_data))
        out = search_result.group(1)
        x = out.split(',{"')
        data = list()
        volume_data = True
        for xi in x:
            xi = re.split(r"\[|:|,|\]", xi)
            ts = datetime.datetime.utcfromtimestamp(float(xi[4]))
            row = [ts]
            for i in range(5, 10):
                # skip converting volume data if does not exists
                if not volume_data and i == 9:
                    row.append(0.0)
                    continue
                try:
                    row.append(float(xi[i]))
                except ValueError:
                    volume_data = False
                    row.append(0.0)
            data.append(row)
        data = pd.DataFrame(data, columns=["datetime", "open", "high", "low", "close", "volume"])
        data = data.set_index("datetime")
        data.insert(0, "symbol", value=symbol)
        return data

    @classmethod
    def format_symbol(cls, symbol: str, exchange: str, fut_contract: tp.Optional[int] = None) -> str:
        """Format a symbol."""
        if ":" in symbol:
            pass
        elif fut_contract is None:
            symbol = f"{exchange}:{symbol}"
        elif isinstance(fut_contract, int):
            symbol = f"{exchange}:{symbol}{fut_contract}!"
        else:
            raise ValueError(f"Invalid fut_contract: '{fut_contract}'")
        return symbol

    def get_hist(
        self,
        symbol: str,
        exchange: str = "NSE",
        interval: str = "1D",
        fut_contract: tp.Optional[int] = None,
        adjustment: str = "splits",
        extended_session: bool = False,
        pro_data: bool = True,
        limit: int = 20000,
        return_raw: bool = False,
    ) -> tp.Union[str, tp.Frame]:
        """Get historical data."""
        symbol = self.format_symbol(symbol=symbol, exchange=exchange, fut_contract=fut_contract)

        backadjustment = False
        if symbol.endswith("!A"):
            backadjustment = True
            symbol = symbol.replace("!A", "!")

        self.create_connection(pro_data=pro_data)
        self.send_message("set_auth_token", [self.auth_token])
        self.send_message("chart_create_session", [self.chart_session, ""])
        self.send_message("quote_create_session", [self.session])
        self.send_message(
            "quote_set_fields",
            [
                self.session,
                "ch",
                "chp",
                "current_session",
                "description",
                "local_description",
                "language",
                "exchange",
                "fractional",
                "is_tradable",
                "lp",
                "lp_time",
                "minmov",
                "minmove2",
                "original_name",
                "pricescale",
                "pro_name",
                "short_name",
                "type",
                "update_mode",
                "volume",
                "currency_code",
                "rchp",
                "rtc",
            ],
        )
        self.send_message("quote_add_symbols", [self.session, symbol, {"flags": ["force_permission"]}])
        self.send_message("quote_fast_symbols", [self.session, symbol])
        self.send_message(
            "resolve_symbol",
            [
                self.chart_session,
                "symbol_1",
                '={"symbol":"'
                + symbol
                + '","adjustment":"'
                + adjustment
                + ("" if not backadjustment else '","backadjustment":"default')
                + '","session":'
                + ('"regular"' if not extended_session else '"extended"')
                + "}",
            ],
        )
        self.send_message("create_series", [self.chart_session, "s1", "s1", "symbol_1", interval, limit])
        self.send_message("switch_timezone", [self.chart_session, "exchange"])

        raw_data = ""
        while True:
            try:
                result = self.ws.recv()
                raw_data += result + "\n"
            except Exception as e:
                break
            if "series_completed" in result:
                break
        if return_raw:
            return raw_data
        return self.convert_raw_data(raw_data, symbol)


class TVData(Data):
    def update_symbol(self, symbol: str, **kwargs):
        download_kwargs = self.select_symbol_kwargs(symbol, self.download_kwargs)
        download_kwargs['start_dt'] = self.data[symbol].index[-1]
        download_kwargs['end_dt'] = download_kwargs['start_dt'] + datetime.timedelta(days=2)
        return self.download_symbol(symbol, **kwargs)

    @classmethod
    def download_symbol(
            cls,
            symbol: str,
            exchange: str = 'NSE',
            interval: str = '1d',
            limit: int = 100,
            retry_count: int = 3,
            **kwargs
    ) -> tp.Frame:
        client = TVClient()
        for _ in range(retry_count):
            try:
                price = client.get_hist(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    limit=limit
                )
                price = price[['open', 'high', 'low', 'close', 'volume']]
                return price
            except Exception as e:
                pass
        raise ValueError('Failed to download symbol')
