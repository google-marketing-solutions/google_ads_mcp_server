**This is not an officially supported Google product.**

# Google Ads MCP

This is the Google Ads Model Context Protocol (MCP) server designed to provide a
standardized way to integrate an LLM with Google Ads.

[![Continuous Integration](https://github.com/google-marketing-solutions/google_ads_mcp_server/actions/workflows/ci.yml/badge.svg)](https://github.com/google-marketing-solutions/google_ads_mcp_server/actions/workflows/ci.yml)
[![Code Style: Google](https://img.shields.io/badge/code%20style-google-4285F4.svg)](https://google.github.io/styleguide/pyguide.html)
[![Conventional Commits](https://img.shields.io/badge/conventional%20commits-1.0.0-fe5196.svg?logo=conventionalcommits)](https://conventionalcommits.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Tools

| Tool            | Parameters             | Description                             |
| --------------- | ---------------------- | --------------------------------------- |
| `list_accounts` |                        | Lists all available Google Ads accounts |
| `search_stream` | `customer_id`, `query` | Runs a Google Ads query                 |

To learn more about GAQL, try out the
[Google Ads Query Builder](https://developers.google.com/google-ads/api/fields/v20/query_validator)
and ensure you have a valid query.

## Setup

### Google Ads

Use
[this documentation](https://developers.google.com/google-ads/api/docs/oauth/service-accounts)
to set up a service account for the Google Ads API client library. This will
require you to also set up a Google Cloud project and enable the Google Ads API.
Create a `google-ads.yaml` file as defined
[here](https://github.com/googleads/google-ads-python/blob/HEAD/google-ads.yaml).
Here's an example:

```yaml
# google-ads.yaml
developer_token: INSERT_DEVELOPER_TOKEN_HERE
login_customer_id: INSERT_LOGIN_CUSTOMER_ID_HERE
json_key_file_path: JSON_KEY_FILE_PATH_HERE
use_proto_plus: true
```

### Server

Run the Google Ads MCP server locally:

```shell
uv run server
```

### Gemini CLI

Install the Gemini CLI by following the instructions
[here](https://github.com/google-gemini/gemini-cli).

Add the Google Ads MCP server to your `~/.gemini/settings.json` file. Here's an
example:

```json
{
  "mcpServers": {
    "googleAds": {
      "command": "uv",
      "args": [
        "--directory path/to/google_ads_mcp",
        "run",
        "server"
      ]
    }
  }
}
```

Learn more about
[MCP servers and Gemini CLI](https://cloud.google.com/gemini/docs/codeassist/use-agentic-chat-pair-programmer#configure-mcp-servers).

## Contributing

Want to contribute? [Learn more](CONTRIBUTING.md)
