# devfest-2025-from-code-to-deployment-build-mcp-tools-for-gemini-and-adk

## Env

```bash
GOOGLE_API_KEY=  # gemini api key
LINE_CHANNEL_SECRET=
LINE_CHANNEL_ACCESS_TOKEN=
```

## Run oo Local 

* install cloudfare tunnel https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/

* Using 

```bash
cloudflared tunnel --url http://127.0.0.1:8001

# get url xxx  https://xxxx.trycloudflare.com 
# use this url in Line Developer Console webhook session
```

## Usage

```bash
make start-webhook
make start-mcp-server
make start-agent-a
```

Use `https://foo.example.tld/webhook` for LINE webhook url.

## Prompt

```bash
what is current weather in new york city
```
