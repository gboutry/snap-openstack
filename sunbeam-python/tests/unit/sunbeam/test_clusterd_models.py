# SPDX-FileCopyrightText: 2024 - Canonical Ltd
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for clusterd models module."""

import json
from unittest.mock import MagicMock

from sunbeam.clusterd.cluster import ClusterService


class TestClusterdModels:
    """Unit tests for clusterd model type hints."""

    def _mock_response(self, status=200, json_data=None, raise_for_status=None):
        """Create a mock response object."""
        mock_resp = MagicMock()
        mock_resp.status_code = status
        if json_data:
            mock_resp.json.return_value = json_data
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        return mock_resp

    def test_list_nodes_returns_node_list(self):
        """Test list_nodes returns list of Node TypedDict."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": [
                {
                    "name": "node-1",
                    "role": ["control"],
                    "machineid": 0,
                    "systemid": "system-1",
                },
                {
                    "name": "node-2",
                    "role": ["compute"],
                    "machineid": 1,
                    "systemid": "system-2",
                },
            ],
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        nodes = cs.list_nodes()

        # Verify return type structure matches Node TypedDict
        assert isinstance(nodes, list)
        assert len(nodes) == 2
        for node in nodes:
            assert "name" in node
            assert "role" in node
            assert "machineid" in node
            assert "systemid" in node
            assert isinstance(node["role"], list)

    def test_get_node_info_returns_node(self):
        """Test get_node_info returns Node TypedDict."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": {
                "name": "node-1",
                "role": ["control", "compute"],
                "machineid": 42,
                "systemid": "sys-abc",
            },
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        node = cs.get_node_info("node-1")

        # Verify return type structure matches Node TypedDict
        assert isinstance(node, dict)
        assert node["name"] == "node-1"
        assert node["role"] == ["control", "compute"]
        assert node["machineid"] == 42
        assert node["systemid"] == "sys-abc"

    def test_list_juju_users_returns_juju_user_list(self):
        """Test list_juju_users returns list of JujuUser TypedDict."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": [
                {"username": "admin", "token": "token1"},
                {"username": "user2", "token": "token2"},
            ],
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        users = cs.list_juju_users()

        # Verify return type structure matches JujuUser TypedDict
        assert isinstance(users, list)
        assert len(users) == 2
        for user in users:
            assert "username" in user
            assert "token" in user

    def test_get_juju_user_returns_juju_user(self):
        """Test get_juju_user returns JujuUser TypedDict."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": {"username": "testuser", "token": "testtoken123"},
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        user = cs.get_juju_user("testuser")

        # Verify return type structure matches JujuUser TypedDict
        assert isinstance(user, dict)
        assert user["username"] == "testuser"
        assert user["token"] == "testtoken123"

    def test_get_terraform_lock_returns_terraform_lock(self):
        """Test get_terraform_lock returns TerraformLock TypedDict."""
        lock_data = {
            "ID": "lock-id-123",
            "Operation": "apply",
            "Info": "Terraform lock info",
            "Who": "user@host",
            "Version": "1.0.0",
            "Created": "2024-01-01T00:00:00Z",
            "Path": "/path/to/plan",
        }
        # Note: The implementation calls json.loads on the raw string response
        # not on the metadata field, so we need to mock accordingly
        json_data = json.dumps(lock_data)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = json_data
        mock_response.text = json_data

        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        lock = cs.get_terraform_lock("test-plan")

        # Verify return type structure matches TerraformLock TypedDict
        assert isinstance(lock, dict)
        assert lock["ID"] == "lock-id-123"
        assert lock["Operation"] == "apply"
        assert lock["Info"] == "Terraform lock info"
        assert lock["Who"] == "user@host"
        assert lock["Version"] == "1.0.0"
        assert lock["Created"] == "2024-01-01T00:00:00Z"
        assert lock["Path"] == "/path/to/plan"

    def test_list_manifests_returns_manifest_list(self):
        """Test list_manifests returns list of Manifest TypedDict."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": [
                {
                    "manifestid": "manifest-1",
                    "data": "manifest data 1",
                    "applied_date": "2024-01-01",
                },
                {
                    "manifestid": "manifest-2",
                    "data": "manifest data 2",
                    "applied_date": None,
                },
            ],
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        manifests = cs.list_manifests()

        # Verify return type structure matches Manifest TypedDict
        assert isinstance(manifests, list)
        assert len(manifests) == 2
        for manifest in manifests:
            assert "manifestid" in manifest
            assert "data" in manifest
            assert "applied_date" in manifest

    def test_get_manifest_returns_manifest(self):
        """Test get_manifest returns Manifest TypedDict."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": {
                "manifestid": "test-manifest",
                "data": "test manifest data",
                "applied_date": "2024-01-15",
            },
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        manifest = cs.get_manifest("test-manifest")

        # Verify return type structure matches Manifest TypedDict
        assert isinstance(manifest, dict)
        assert manifest["manifestid"] == "test-manifest"
        assert manifest["data"] == "test manifest data"
        assert manifest["applied_date"] == "2024-01-15"

    def test_get_server_certpair_returns_certpair(self):
        """Test get_server_certpair returns CertPair TypedDict."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": {
                "certificate": "-----BEGIN CERTIFICATE-----\ntest\n-----END CERTIFICATE-----",
                "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
            },
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        certpair = cs.get_server_certpair()

        # Verify return type structure matches CertPair TypedDict
        assert isinstance(certpair, dict)
        assert "certificate" in certpair
        assert "private_key" in certpair
        assert certpair["certificate"].startswith("-----BEGIN CERTIFICATE-----")
        assert certpair["private_key"].startswith("-----BEGIN PRIVATE KEY-----")

    def test_get_status_returns_member_status_dict(self):
        """Test get_status returns dict[str, MemberStatus]."""
        json_data = {
            "type": "sync",
            "status": "Success",
            "status_code": 200,
            "metadata": [
                {"name": "node-1", "status": "ONLINE", "address": "10.0.0.1:7000"},
                {"name": "node-2", "status": "ONLINE", "address": "10.0.0.2:7000"},
            ],
        }
        mock_response = self._mock_response(status=200, json_data=json_data)
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response

        cs = ClusterService(mock_session, "http+unix://mock")
        status = cs.get_status()

        # Verify return type structure matches dict[str, MemberStatus]
        assert isinstance(status, dict)
        assert "node-1" in status
        assert "node-2" in status
        for member_name, member_status in status.items():
            assert "status" in member_status
            assert "address" in member_status
            assert isinstance(member_status["status"], str)
            assert isinstance(member_status["address"], str)
