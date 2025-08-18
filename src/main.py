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
A Google Ads MCP server.
"""

import os
from typing import Iterable, List, MutableSequence

from fastmcp import FastMCP
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.v20.services.services.customer_service.client import (
    CustomerServiceClient,
)
from google.ads.googleads.v20.services.services.google_ads_service import (
    GoogleAdsServiceClient,
)
from google.ads.googleads.v20.services.types.customer_service import (
    ListAccessibleCustomersResponse,
)
from google.ads.googleads.v20.services.types.google_ads_service import (
    GoogleAdsRow,
    SearchGoogleAdsStreamResponse,
)

mcp = FastMCP("Google Ads")

_CLIENT: GoogleAdsClient | None = None


def get_client() -> GoogleAdsClient:
    """Initializes and returns the Google Ads client, cached for reuse."""
    global _CLIENT
    if _CLIENT is None:
        os.environ["GOOGLE_ADS_CONFIGURATION_FILE_PATH"] = "./google-ads.yaml"
        _CLIENT = GoogleAdsClient.load_from_storage()
    return _CLIENT


@mcp.tool
def list_accounts():
    client = get_client()
    customer_service: CustomerServiceClient = client.get_service(
        "CustomerService"
    )
    accessible_customers: ListAccessibleCustomersResponse = (
        customer_service.list_accessible_customers()
    )
    return type(accessible_customers).to_json(accessible_customers)


@mcp.tool
def search_stream(
    customer_id: str,
    query: str,
    login_customer_id: str | None = None,
):
    client = get_client()
    if login_customer_id:
        client.login_customer_id = login_customer_id
    service: GoogleAdsServiceClient = client.get_service("GoogleAdsService")
    stream: Iterable[SearchGoogleAdsStreamResponse] = service.search_stream(
        customer_id=customer_id,
        query=query,
    )
    results: List[str] = []
    for batch in stream:
        rows: MutableSequence[GoogleAdsRow] = batch.results
        for row in rows:
            results.append(type(row).to_json(row))
    return results


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
