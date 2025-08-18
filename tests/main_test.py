# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for the Google Ads MCP server.
"""

import json
from unittest.mock import MagicMock, PropertyMock

import pytest
from fastmcp import Client
from google.ads.googleads.v20.services.types.customer_service import (
    ListAccessibleCustomersResponse,
)
from google.ads.googleads.v20.services.types.google_ads_service import (
    SearchGoogleAdsStreamResponse,
)
from mcp.types import TextContent

from src.main import mcp

pytestmark = pytest.mark.asyncio


@pytest.fixture(name="mock_client")
def fixture_mock_client(monkeypatch):
    """Provides a mock GoogleAdsClient."""
    client = MagicMock()
    client.customer_service = MagicMock()
    client.google_ads_service = MagicMock()
    service_map = {
        "CustomerService": client.customer_service,
        "GoogleAdsService": client.google_ads_service,
    }
    client.get_service.side_effect = service_map.get
    monkeypatch.setattr("src.main.get_client", lambda: client)
    return client


class TestListAccounts:
    """
    Test the list_accounts tool.
    """

    async def test_returns_customers(self, monkeypatch, mock_client):
        """Tests that the tool returns a list of customer resource names."""
        resource_names = ["customers/8885555555", "customers/8005882300"]
        expected_json = json.dumps({"resourceNames": resource_names})
        monkeypatch.setattr(
            ListAccessibleCustomersResponse,
            "to_json",
            lambda *a, **kw: expected_json,
        )
        mock_response = ListAccessibleCustomersResponse(
            resource_names=resource_names
        )
        (
            mock_client.customer_service.list_accessible_customers.return_value
        ) = mock_response
        async with Client(mcp) as client:
            result = await client.call_tool("list_accounts")
        assert isinstance(result.content[0], TextContent)
        assert result.content[0].text == expected_json

    async def test_returns_empty_list_for_no_customers(
        self, monkeypatch, mock_client
    ):
        """
        Tests that the tool returns an empty list when no customers are
        accessible.
        """
        expected_json = json.dumps({"resourceNames": []})
        monkeypatch.setattr(
            ListAccessibleCustomersResponse,
            "to_json",
            lambda *a, **kw: expected_json,
        )
        mock_response = ListAccessibleCustomersResponse(resource_names=[])
        (
            mock_client.customer_service.list_accessible_customers.return_value
        ) = mock_response
        async with Client(mcp) as client:
            result = await client.call_tool("list_accounts")
        assert isinstance(result.content[0], TextContent)
        assert result.content[0].text == expected_json


class TestSearchStream:
    """
    Test the search_stream tool.
    """

    class MockGoogleAdsRow:
        """A mock for the GoogleAdsRow object."""

        def __init__(self, campaign_id, campaign_name):
            self.campaign = MagicMock()
            self.campaign.id = campaign_id
            self.campaign.name = campaign_name

        @classmethod
        def to_json(cls, instance):
            """Mocks the to_json method."""
            return json.dumps({
                "campaign": {
                    "id": instance.campaign.id,
                    "name": instance.campaign.name,
                }
            })

    async def test_returns_rows_from_stream(self, mock_client):
        """Tests that the tool returns serialized rows from the stream."""
        mock_row_1 = self.MockGoogleAdsRow(111, "Campaign 1")
        mock_row_2 = self.MockGoogleAdsRow(222, "Campaign 2")

        mock_batch = MagicMock(
            spec=SearchGoogleAdsStreamResponse, results=[mock_row_1, mock_row_2]
        )
        mock_client.google_ads_service.search_stream.return_value = [mock_batch]

        async with Client(mcp) as client:
            result = await client.call_tool(
                "search_stream",
                {
                    "customer_id": "1234567890",
                    "query": "SELECT campaign.id, campaign.name FROM campaign",
                },
            )

        expected_list = json.dumps(
            [
                type(mock_row_1).to_json(mock_row_1),
                type(mock_row_2).to_json(mock_row_2),
            ],
            separators=(",", ":"),
        )
        assert isinstance(result.content[0], TextContent)
        assert result.content[0].text == expected_list

    async def test_sets_login_customer_id_when_provided(self, mock_client):
        """Tests that the login_customer_id is correctly set on the client."""
        mock_client.google_ads_service.search_stream.return_value = []

        login_customer_id_mock = PropertyMock()
        type(mock_client).login_customer_id = login_customer_id_mock

        login_customer_id = "8008675309"
        async with Client(mcp) as client:
            await client.call_tool(
                "search_stream",
                {
                    "customer_id": "1234567890",
                    "query": "SELECT campaign.id, campaign.name FROM campaign",
                    "login_customer_id": login_customer_id,
                },
            )

        login_customer_id_mock.assert_called_once_with(login_customer_id)

    async def test_handles_empty_stream(self, mock_client):
        """Tests that the tool returns an empty list for an empty stream."""
        mock_client.google_ads_service.search_stream.return_value = []

        async with Client(mcp) as client:
            result = await client.call_tool(
                "search_stream",
                {
                    "customer_id": "1234567890",
                    "query": "SELECT campaign.id, campaign.name FROM campaign",
                },
            )

        assert result.content == []
