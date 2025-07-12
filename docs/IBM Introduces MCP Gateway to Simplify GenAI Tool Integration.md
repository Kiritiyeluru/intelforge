IBM has launched MCP Gateway, a FastAPI-based component designed to streamline the integration and orchestration of generative AI tools and services. It is an open-source project made available under the Apache 2.0 license. 

The gateway is built on the model context protocol (MCP) and supports a wide range of transports, including HTTP/JSON-RPC, WebSocket, Server-Sent Events (SSE), and stdio. It allows users to federate multiple MCP servers into a unified endpoint and wrap any REST API or function as a virtual MCP-compliant tool.

Armand Ruiz, VP of AI platform at IBM, stated on LinkedIn, “I think this is a great step forward for those building agentic systems, orchestrating tools, or deploying complex GenAI apps.”

IBM describes it as a central gateway used to manage tool, resource, and prompt registries, adhering to the official MCP 25-03-26 protocol, as per its GitHub page. It enables auto-discovery of peer servers, virtualises non-MCP services, and integrates input validation, retry logic, and rate-limiting features for REST endpoints.

The offering also includes a production-ready admin UI built with HTMX and Tailwind, supporting full CRUD operations and observability out of the box. Authentication schemes such as Basic, JWT, and custom headers are supported, along with async database persistence via SQLAlchemy.

IBM also recently introduced a draft for a new agent communication protocol (ACP) aimed at standardising how AI agents interact and collaborate across systems. Positioned as something to complement MCP, ACP addresses the former’s limitations by making agents core participants rather than secondary elements. 

Currently in its pre-alpha phase, ACP focuses on integration, communication, and collaboration between agents, with future standardisation contingent on adoption. The protocol is part of IBM’s BeeAI initiative, and the company is actively engaging developers through GitHub to refine its architecture. 

ACP follows similar efforts by Anthropic, whose MCP implementation enabled integration with popular APIs like Spotify and Google Maps.

Considering IBM’s related development, it reflects a broader push towards standardising AI infrastructure, aiming to reduce friction in tool orchestration and deployment at scale.