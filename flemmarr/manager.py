import requests
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry


class APIManager:
    def __init__(self, address, port):
        self.address = self._format_address(address)
        self.port = port
        self.path = ""

        self.session = requests.Session()
        self._setup_retries()

    @staticmethod
    def _format_address(address):
        if not address.startswith("http"):
            return f"http://{address}"
        return address

    def _setup_retries(self):
        retry_strategy = Retry(
            total=10,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _url(self, resource="", id=None):
        id_path = f"/{id}" if id else ""
        return f"{self.address}:{self.port}{self.path}{resource}{id_path}"

    def _handle_response(self, response: Response, action, resource, id=None):
        id_string = f" {id}" if id else ""
        if response.status_code < 300:
            print(f"{action} {resource}{id_string}: {response.status_code}")
            return response.json()
        else:
            print(f"Error {action.lower()} {resource}{id_string}: {response.status_code}")
            response.raise_for_status()

    def _get(self, resource, id=None):
        response = self.session.get(self._url(resource, id))
        return self._handle_response(response, "Fetching", resource, id)

    def _create(self, resource, body):
        response = self.session.post(self._url(resource), json=body)
        return self._handle_response(response, "Creating", resource)

    def _edit(self, resource, body, id=None):
        current_data = self._get(resource, id)
        updated_data = {**current_data, **body}

        response = self.session.put(self._url(resource, id), json=updated_data)
        self._handle_response(response, "Editing", resource, id)

    def _delete(self, resource, id):
        response = self.session.delete(self._url(resource, id))
        self._handle_response(response, "Deleting", resource, id)

    def _triage_and_apply(self, obj, resource=""):
        if isinstance(obj, dict):
            if any(isinstance(obj[key], (dict, list)) for key in obj):
                for key, value in obj.items():
                    self._triage_and_apply(value, f"{resource}/{key}")
            else:
                self._edit(resource, obj)
        elif isinstance(obj, list):
            for body in obj:
                self._create(resource, body)

    def initialize(self):
        response = self.session.get(f"{self._url()}/initialize.json")
        if response.status_code != 200:
            print("Failed to initialize API connection.")
            response.raise_for_status()

        data = response.json()
        print(data)
        self.path = data["apiRoot"]
        self.session.headers.update({"X-Api-Key": data["apiKey"]})

        print("Successfully connected to the server and fetched the API key and path.")

    def apply(self, config):
        self._triage_and_apply(config)
