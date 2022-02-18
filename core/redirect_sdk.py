from typing import List
from datetime import datetime
import os
import pprint
import typing
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse

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


class InvalidAuth(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.pre = "Failed to authenticate with the provided credentials!"
        self.message = f"{self.pre}: Response Code: {self.status_code}."
        super().__init__(self.message)


class RedirectClient:
    def __init__(self, token: str, domain: str = None):
        """Initializes the RedirectObject class.

        Args:
            token (str): The authorization token.
            domain (str, optional): The domain to use. Defaults to None.
        """
        self.token = token
        self.domain = domain

    def get_redirects(self) -> List[RedirectPizza]:
        """Returns a list of redirects

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            list: List of redirects.
        """
        r = requests.get(
            "https://redirect.pizza/api/v1/redirects", auth=("bearer", self.token)
        )
        if r.status_code == 422:
            raise InvalidAuth(r.status_code)
        data = r.json()
        data = data["data"]
        ListData = []
        for object in range(len(data) - 1):
            # object = object
            FullURL = data[object]["sources"][object]["url"]
            ParsedDomain = urlparse(FullURL)
            Domain = ParsedDomain.netloc
            Path = ParsedDomain.path

            ListData.append(
                RedirectPizza(
                    r.json()["data"][object]["id"],
                    Domain,
                    Path,
                    r.json()["data"][object]["destination"],
                    r.json()["data"][object]["created_at"],
                )
            )
        return ListData

    def fetch_redirect(self, r_id: str) -> RedirectPizza:
        """Fetches a redirect.

        Args:
            url_code (str): The URL code to fetch.
            domain (str, optional): The domain to use. Defaults to None.

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            typing.Union[dict, int]: Returns a dict of the redirect or an int of the status code.
        """

        r = requests.get(
            f"https://redirect.pizza/api/v1/redirects/{r_id}",
            auth=("bearer", self.token),
        )
        if r.status_code == 422:
            raise InvalidAuth(r.status_code)
        object = range(len(r.json()))

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

    def add_redirect(
        self, redirect_url: str, destination: str, domain: str = None
    ) -> RedirectPizza:
        """Adds a redirect.

        Args:
            redirect_url (str): The URL to redirect.
            destination (str): The destination URL.
            domain (str, optional): The domain to use. Defaults to None.

        Raises:
            InvalidAuth: [description]

        Returns:
            typing.Union[dict, int]: Returns a dict of the redirect or an int of the status code.
        """
        print(redirect_url, destination, domain)
        if domain is None and self.domain is None:
            raise TypeError("Domain is not set!")
        if domain is None and self.domain is not None:
            domain = self.domain

        r = requests.post(
            "https://redirect.pizza/api/v1/redirects",
            auth=("bearer", self.token),
            json={
                "sources": f"{domain}/{redirect_url}",
                "destination": destination,
                "redirect_type": "permanent",
                "uri_forwarding": False,
                "keep_query_string": False,
                "tracking": True,
            },
        )
        if r.status_code == 422:
            raise InvalidAuth(r.status_code)
        print(r.status_code)
        object = range(len(r.json()["data"]))
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

    def del_redirect(self, r_id: str) -> typing.Union[dict, int]:
        """Deletes a redirect.

        Args:
            redirect_url (str): The URL to delete.
            domain (str, optional): The domain to use. Defaults to None.

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            typing.Union[dict, int]: Returns a dict of the redirect or an int of the status code.
        """

        r = requests.delete(
            f"https://redirect.pizza/api/v1/redirects/{r_id}",
            auth=("bearer", self.token),
        )
        print(r.status_code)
        if r.status_code == 422:
            raise InvalidAuth(r.status_code)
        return r.status_code
