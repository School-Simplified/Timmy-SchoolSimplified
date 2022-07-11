from __future__ import annotations

import pprint
import typing
from datetime import datetime
from typing import List, TYPE_CHECKING
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

if TYPE_CHECKING:
    pass

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
            raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])

        last_page = r.json()["meta"]["last_page"]
        list_of_data = []
        for page in range(1, last_page + 1):
            r = requests.get(
                    f"https://redirect.pizza/api/v1/redirects?page={page}",
                    auth=("bearer", self.token),
            )

            data = r.json()["data"]
            for num in range(len(data) - 1):
                """Iterates through the data and creates a list of redirects."""
                full_url = data[num]["sources"][0]["url"]
                parsed_link = urlparse(full_url)
                domain = parsed_link.netloc
                url_path = parsed_link.path

                list_of_data.append(
                    RedirectPizza(
                        r.json()["data"][num]["id"],
                        domain,
                        url_path,
                        r.json()["data"][num]["destination"],
                        r.json()["data"][num]["created_at"],
                    )
                )
        return list_of_data

    def fetch_redirect(self, r_id: str, subdomain: str = None) -> typing.Union[RedirectPizza, None]:
        """Fetches a redirect.

        Args:
            r_id (str): The URL code to fetch.
            subdomain (str, optional): The subdomain to use. Defaults to None.

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
            raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])

        elif r.status_code == 404:
            if "ssimpl.org" not in r_id:
                r_id = f"ssimpl.org/{r_id}"
            elif subdomain is not None and "ssimpl.org" not in r_id:
                r_id = f"{subdomain}.ssimpl.org/{r_id}"

            redirects = self.get_redirects()
            for redirect in redirects:
                if redirect.source == r_id:
                    return redirect

        try:
            if len(list(r.json()["data"]["sources"])) > 1:
                full_url = r.json()["data"]["sources"][0]["url"]
            else:
                full_url = r.json()["data"]["sources"]["url"]
        except KeyError:
            return None
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

    def add_redirect(
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
            }
        )
        if r.status_code == 422:
            raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])
        pprint.pprint(r.json())

        full_url = r.json()["data"]["sources"][0]["url"]
        parsed_domain = urlparse(full_url)
        domain_value = parsed_domain.netloc
        path = parsed_domain.path

        return RedirectPizza(
            r.json()["data"]["id"],
            domain_value,
            path,
            r.json()["data"]["destination"],
            r.json()["data"]["created_at"],
        )

    def del_redirect(self, id_or_path: str, sub_domain: str = None) -> int:
        """Deletes a redirect.

        Args:
            id_or_path (str): The URL code to delete.
            sub_domain (str, optional): The subdomain to use. Defaults to None.

        Raises:
            InvalidAuth: Invalid authorization key passed in.

        Returns:
            typing.Union[dict, int]: Returns a dict of the redirect or an int of the status code.
        """

        try:
            int(id_or_path)
        except ValueError:
            found = False
            self.get_redirects()
            if "ssimpl.org" not in id_or_path and sub_domain is None:
                id_or_path = f"ssimpl.org/{id_or_path}"
            elif sub_domain is not None and "ssimpl.org" not in id_or_path:
                id_or_path = f"{sub_domain}.ssimpl.org/{id_or_path}"
            for redirect in self.get_redirects():
                if redirect.source == id_or_path:
                    id_or_path = redirect.id
                    found = True
                    break
            if not found:
                raise ValueError(f"Could not find redirect with path {id_or_path}")

        r = requests.delete(
                f"https://redirect.pizza/api/v1/redirects/{id_or_path}",
                auth=("bearer", self.token),
        )
        if r.status_code == 422:
            raise UnprocessableEntity(r.status_code, r.json()["message"], r.json()["errors"])
        return r.status_code
