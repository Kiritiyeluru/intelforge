Run MCP Servers In Seconds With Docker
#
ai
#
docker
#
mcp
#
llm
Model Context Protocol (MCP) has taken the AI world by storm. It has become the de facto standard for how an AI Agent connect with tools, services, and data. As this is shaping up rapidly, working with different MCP servers, setting them up is still not an easy task, and it requires a learning curve. Docker has a track record of making developers’ lives easier to make, build and ship things faster and again it chimes in to the MCP space, bringing that same clarity, trust, and scalability. That’s exactly what Docker is doing with and introduction of Docker MCP Catalog and Docker MCP Toolkit after the Docker Model Runner (if you haven’t checked it out, here is the link).

In this blog, we will first under what Docker MCP Catalog and MCP Toolkit are. Then we will see step-by-step how we can use Docker MCP Toolkit using Docker Desktop to interact with various tools using MCP Clients offered by Claude, Cursor, etc.

What is Docker MCP Catalog?
Docker MCP Catalog is a trusted collection of MCP servers. Currently has verified tools from 100 verified (and the number keeps bumping while writing this) tools publishers like Stripe, Elastic, Grafana, etc. And the tools are it’s just like container images, that means like traditional pull mechanism, we can pull and use it (or use MCP toolkit for UI perks, more on that later) without any hassle to find and configure it manually.

mcp server list website

What is Docker MCP Toolkit?
With Docker MCP Toolkit, with a single click of a button from Docker Desktop, we can spin MCP servers in seconds and connect to our favourite client like Cluade, Cursor, Windsurf, Docker AI Agent, etc. The way it works is that a Gateway MCP Server is created and dynamically exposes enabled tools to compatible clients. This makes it so easy to manage all the tools in one place.

mcp server list docker desktop

Using Docker MCP Toolkit
Let’s now test Docker MCP Toolkit. Make sure you have the latest version of Docker Desktop. My current version is Docker Desktop (Mac) is 4.43.0 (196668). Once you open it, you will see the MCP Toolkit button on the sidebar. Initially, it was shipped as an extension; now it’s baked into the Docker Desktop itself.

mcp docker desktop catalog

Now let’s install/turn on some MCP servers like curl and Wikipedia. You can search and add it. It’s that simple. It’s really handy to add and remove when needed. No copying and pasting of manual config, and managing them.

mcp tookit tools

Now, let’s connect the Dockerized MCP servers to our MCP clients. I will be using Claude; you can use any according to your preference. We simply need to click on the Connect button, and it will automatically add the Docker configuration to Claude Code's MCP server config claude_desktop_config.json file. The same goes for other MCP Clients.

tool clients

Let’s open Claude and see it. It will be Settings > Developer > MCP_DOCKER. As you can see, it’s running, which means everything is correctly configured. If we click on the Edit Config button, we can see the config and how it works.

claude mcp <br>
![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/sefrakhw7nzvuybmeb77.png)config

Config:

{
   "mcpServers":{
      "MCP_DOCKER":{
         "command":"docker",
         "args":[
            "mcp",
            "gateway",
            "run"
         ]
      }
   }
}
Let’s close the config and open the chat screen on Claude. Now, click on the Search and Tools option to see all the MCP servers, for just, it’s just one, MCP_DOCKER,, having 10 tools. If you are not seeing it, completely close down Claude and re-open it, and it will start showing up.

!
cluade desktop

We can click on the arrow next to 10 to see all the available tools.

tools list

Now, let’s test it out.

To test curl, I will ask whether the website is up or not. When you enter the prompt, you might get a pop-up saying “Claude would like to use an external integration”; it is just to determine whether you want to use the MCP tools or not. You can either choose, always allow or allow once, depending on your preference.

curl test

Let’s now search for some history so that it uses the Wikipedia tool. As you can see, it is called both search_wikipedia and get_wikipedia and gives the result.