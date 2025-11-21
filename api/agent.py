from rag.agent_core import get_agent

_agent = None

async def load_agent():
    global _agent
    if _agent is None:
        _agent = get_agent()
    return _agent

async def chat(message: str) -> str:
    agent = await load_agent()
    response = await agent.run(message)
    return str(response)
