Okay as a senior dev, I seemed to have learned this lesson late with Claude Code.

If you want good results, find a way to structure your code base in a way that makes logical sense to Claude.

I'm a React Next.js dev, and the worst thing about this stack is that it's constantly changing. There's not "one" way to do things. Honestly I wish someone would just make an LLM friendly framework, but alas.

So previously I've been just pretty loose with the file structure, trying to use a combination of server actions, api routes, lib and utility files, without really a rhyme or reason as to which files go where and how they are structured. Lots of individual utility functions spread out everywhere. Consuming endpoints in react hooks, some context in tanstack query, some in local state, some in zustand. In short, a mess.

Anyways, lately I decided enough was enough, and decided to pull the trigger with oRPC. You may already be using tRPC, and I don't know the big difference between the two, but basically oRPC is similar, just that its built on OpenAPI standards (not openAI).

Front and back are fully typesafe, uses tanstack query to cache and fetch... but most importantly, groups everything logically.
Routers are where you define your input and output typesafe contracts. They then call out to services. Services will use 'repositories' to query the db. From there, you can built out any number of patterns. I've started using engines, processors, utilities, algos, strategies...
But the interesting thing is that you add this to the file name.
translation.strategy.ts
translation.router.ts
translation.repository.ts

etc.

This seems to give claude a ton of context just with the filename, and along with a few examples from the docs, it's been refactoring my entire app basically in one shot without bugs and perfect types. Green files in vscode.

Honestly, I'm super happy with it. Ctrl Clicking function names that bring you to the implementation right from the react frontend files is amazing, and clearly it makes sense for Claude.

Check it out: https://orpc.unnoq.com/docs/getting-started