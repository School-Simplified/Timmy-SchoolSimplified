from __future__ import annotations

import pprint
import typing
from datetime import datetime
from typing import List, TYPE_CHECKING
from urllib.parse import urlparse

from dotenv import load_dotenv

if TYPE_CHECKING:
    from main import Timmy

"""[summary]

    Raises:
        InvalidAuth: [description]
        InvalidAuth: [description]
        TypeError: [description]
        InvalidAuth: [description]
        InvalidAuth: [description]

    Returns:
        [type]: [description]
"""

load_dotenv()


def cleanup_url(url: str) -> str:
    """Cleans up the text to be a valid URL.

    Returns:
        str: The cleaned up URL.
    """
    url = url.replace(" ", "-")
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return f"https://{url}"


class RedirectPizza:
    def __init__(
            self, id: int, domain: str, source: str, destination: str, created_at: datetime
    ) -> None:
        self.id = id
        self.domain = domain
        self.source = source
        self.destination = destination
        self.created_at = created_at


class UnprocessableEntity(Exception):
    def __init__(self, status_code: int, message: str, errors: list[str]) -> None:
        self.status_code = status_code
        self.message = message
        self.errors = errors
        self.pre = "Unprocessable Entity"
        self.message = f"{self.pre}: {self.message}\n  -> Response Code: {self.status_code}."
        super().__init__(self.message)


class RedirectClient:
    def __init__(self, token: str, bot: Timmy, domain: str = None):
        """Initializes the RedirectObject class.

        Args:
            token (str): The authorization token.
            domain (str, optional): The domain to use. Defaults to None.
        """
        self.token = token
        self.domain = domain
        self.bot = bot

    async def get_redirects(self) -> List[RedirectPizza]:
        """Returns a list of redirects

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            list: List of redirects.
        """
        async with self.bot.session.get(
                "https://redirect.pizza/api/v1/redirects", auth=("bearer", self.token)
        ) as r:
            if r.status_code == 422:
                raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])
            data = r.json()
        pprint.pprint(data)
        # for data in range(len(data["data"])):
        data = data["data"]
        ListData = []
        for object in range(len(data) - 1):
            """Iterates through the data and creates a list of redirects."""
            full_url = data[object]["sources"][0]["url"]
            parsed_link = urlparse(full_url)
            domain = parsed_link.netloc
            url_path = parsed_link.path

            ListData.append(
                RedirectPizza(
                    r.json()["data"][object]["id"],
                    domain,
                    url_path,
                    r.json()["data"][object]["destination"],
                    r.json()["data"][object]["created_at"],
                )
            )
        return ListData

    async def fetch_redirect(self, r_id: str) -> RedirectPizza:
        """Fetches a redirect.

        Args:
            r_id (str): The URL code to fetch.

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            typing.Union[dict, int]: Returns a dict of the redirect or an int of the status code.
        """
        async with self.bot.session.get(
                f"https://redirect.pizza/api/v1/redirects/{r_id}",
                auth=("bearer", self.token),
        ) as r:
            print(r.json(), r.status_code)
            if r.status_code == 422:
                raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])
            elif r.status_code == 404:
                if "ssimpl.org" not in r_id:
                    r_id = f"ssimpl.org/{r_id}"
                redirects = self.get_redirects()
                for redirect in redirects:
                    print(redirect.source)
                    if redirect.source == r_id:
                        return redirect

        full_url = r.json()["data"]["sources"]["url"]
        parsed_domain = urlparse(full_url)
        domain = parsed_domain.netloc
        path = parsed_domain.path

        return RedirectPizza(
            r.json()["data"]["id"],
            domain,
            path,
            r.json()["data"]["destination"],
            r.json()["data"]["created_at"],
        )

    async def add_redirect(
            self, redirect_url: str, destination: str, domain: str = None
    ) -> RedirectPizza:
        """Adds a redirect.

        Args:
            redirect_url (str): The URL to redirect.
            destination (str): The destination URL.
            domain (str, optional): The domain to use. Defaults to None.

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            typing.Union[dict, int]: Returns a dict of the redirect or an int of the status code.
        """
        if domain is None and self.domain is None:
            raise TypeError("Domain is not set!")
        if domain is None and self.domain is not None:
            domain = self.domain
        async with self.bot.session.post(
                "https://redirect.pizza/api/v1/redirects",
                auth=("bearer", self.token),
                json={
                    "sources": f"{domain}/{redirect_url}",
                    "destination": destination,
                    "redirect_type": "permanent",
                    "uri_forwarding": False,
                    "keep_query_string": False,
                    "tracking": True,
                }
        ) as r:
            if r.status_code == 422:
                raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])
            pprint.pprint(r.json())

        FullURL = r.json()["data"]["sources"][0]["url"]
        ParsedDomain = urlparse(FullURL)
        Domain = ParsedDomain.netloc
        Path = ParsedDomain.path

        return RedirectPizza(
            r.json()["data"]["id"],
            Domain,
            Path,
            r.json()["data"]["destination"],
            r.json()["data"]["created_at"],
        )

    async def del_redirect(self, r_id: str) -> typing.Union[dict, int]:
        """Deletes a redirect.

        Args:
            redirect_url (str): The URL to delete.
            domain (str, optional): The domain to use. Defaults to None.

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            typing.Union[dict, int]: Returns a dict of the redirect or an int of the status code.
        """
        async with self.bot.session.delete(
                f"https://redirect.pizza/api/v1/redirects/{r_id}",
                auth=("bearer", self.token),
        ) as r:
            print(r.status_code)
            if r.status_code == 422:
                raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])
            return r.status_code
