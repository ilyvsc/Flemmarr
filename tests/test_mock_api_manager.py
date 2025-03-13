import unittest
from unittest.mock import Mock, call, patch

from requests.exceptions import HTTPError

from flemmarr.manager import APIManager


class TestMockAPIManager(unittest.TestCase):
    def setUp(self):
        self.session_patcher = patch("requests.Session")
        self.mock_session_class = self.session_patcher.start()
        self.mock_session = self.mock_session_class.return_value
        self.url = "http://localhost:8989"
        self.manager = APIManager("localhost", 8989)
        self.manager.session.headers.update({"X-Api-Key": "test-key"})

    def tearDown(self):
        self.session_patcher.stop()

    def test_initialize_success(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"apiKey": "new-key", "apiRoot": "/api/v2"}
        self.mock_session.get.return_value = mock_response

        self.manager.session.headers.update.reset_mock()
        self.manager.initialize()

        self.mock_session.get.assert_called_once_with(f"{self.url}/initialize.json")
        self.assertEqual(self.manager.path, "/api/v2")
        self.manager.session.headers.update.assert_called_once_with(
            {"X-Api-Key": "new-key"}
        )

    def test_initialize_failure(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("Not found")
        self.mock_session.get.return_value = mock_response

        with self.assertRaises(HTTPError):
            self.manager.initialize()

    def test_get_request_success(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1}
        self.mock_session.get.return_value = mock_response

        result = self.manager._get("/test", 1)
        self.assertEqual(result, {"id": 1})
        self.mock_session.get.assert_called_once_with(f"{self.url}/test/1")

    def test_get_request_error(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("Not found")
        self.mock_session.get.return_value = mock_response

        with self.assertRaises(HTTPError):
            self.manager._get("/missing")

    def test_create_resource(self):
        mock_response = Mock()
        mock_response.status_code = 201
        self.mock_session.post.return_value = mock_response

        self.manager._create("/resource", {"name": "test"})
        self.mock_session.post.assert_called_once_with(
            f"{self.url}/resource", json={"name": "test"}
        )

    def test_edit_resource(self):
        existing_data_mock = Mock()
        existing_data_mock.status_code = 200
        existing_data_mock.json.return_value = {"id": 1, "name": "old"}
        self.mock_session.get.return_value = existing_data_mock

        put_mock = Mock()
        put_mock.status_code = 200
        self.mock_session.put.return_value = put_mock

        self.manager._edit("/resource", {"name": "new"}, 1)

        self.mock_session.put.assert_called_once_with(
            f"{self.url}/resource/1", json={"id": 1, "name": "new"}
        )

    def test_delete_resource(self):
        delete_mock = Mock()
        delete_mock.status_code = 200
        self.mock_session.delete.return_value = delete_mock

        self.manager._delete("/resource", 1)
        self.mock_session.delete.assert_called_once_with(f"{self.url}/resource/1")

    def test_triage_and_apply_nested_dict(self):
        config = {"config": {"naming": {"renameEpisodes": True}}}

        with patch.object(self.manager, "_edit") as mock_edit:
            self.manager._triage_and_apply(config)
            mock_edit.assert_has_calls([call("/config/naming", {"renameEpisodes": True})])

    def test_triage_and_apply_list(self):
        config = [{"name": "client1"}, {"name": "client2"}]

        with patch.object(self.manager, "_create") as mock_create:
            self.manager._triage_and_apply(config, "/downloadclient")
            mock_create.assert_has_calls(
                [
                    call("/downloadclient", {"name": "client1"}),
                    call("/downloadclient", {"name": "client2"}),
                ]
            )

    def test_apply_full_config(self):
        config = {
            "downloadclient": [{"name": "qbittorrent"}],
            "config/naming": {"standardEpisodeFormat": "S{season}E{episode}"},
        }

        with patch.object(self.manager, "_triage_and_apply") as mock_triage:
            self.manager.apply(config)
            mock_triage.assert_called_once_with(config)

    def test_url_construction(self):
        test_cases = [
            (("/resource", None), f"{self.url}/resource"),
            (("/resource", 1), f"{self.url}/resource/1"),
            (("/sub/resource", 5), f"{self.url}/sub/resource/5"),
        ]

        for (resource, id), expected in test_cases:
            with self.subTest(resource=resource, id=id):
                self.assertEqual(self.manager._url(resource, id), expected)


if __name__ == "__main__":
    unittest.main()
