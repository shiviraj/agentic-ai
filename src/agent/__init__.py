import asyncio
import os
import pathlib
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from fastmcp import Client as MCPClient
from ollama import Client as OllamaClient
from prompt_toolkit import PromptSession
from rich.console import Console

from agent.application.service.analyze_task_service import AnalyzeTaskService
from agent.application.service.summarize_agent_service import SummarizeAgentService
from agent.application.service.tool_executor import ToolExecutor
from agent.application.workflow.engineer_agent_service import EngineerAgentService
from agent.application.workflow.query_agent_service import QueryAgentService
from agent.application.workflow.task_agent_service import TaskAgentService
from agent.domain.aggregate.conversation import Conversation
from agent.domain.policy.task_analysis_policy import TaskAnalysisPolicy
from agent.domain.tool.tool_registry import ToolRegistry
from agent.infrastructure.agents.engineer_agent_impl import EngineerAgentImpl
from agent.infrastructure.agents.query_agent_impl import QueryAgentImpl
from agent.infrastructure.agents.summary_agent_impl import SummaryAgentImpl
from agent.infrastructure.agents.task_agent_impl import TaskAgentImpl
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl
from agent.infrastructure.mcp.tool_provider_impl import ToolProviderImpl
from agent.infrastructure.persistence.conversation_repository_impl import ConversationRepositoryImpl
from agent.infrastructure.prompts.prompt_loader import load_prompt
from agent.interface.cli.user_input import create_prompt_session, user_request
from agent.shared.logger.logger import Logger


async def main() -> None:
    logger = Logger("Main")
    load_dotenv()
    model = os.getenv("MODEL")
    host = os.getenv("API_URL")
    timeout = int(os.getenv("TIMEOUT", "60"))

    conversation = Conversation.create()
    conversation_repository = ConversationRepositoryImpl()
    conversation_repository.save(conversation)

    ollama_client = OllamaClient(host=host, timeout=timeout)
    llm_client = LLMClientImpl(client=ollama_client, model=model)

    session: PromptSession[str] = create_prompt_session()
    console = Console()
    console.print(f"[cyan]{load_prompt('instruction')}[/cyan]")

    mcp_client = MCPClient(pathlib.Path("src/agent/infrastructure/mcp/server/filesystem_server.py"))
    exit_stack = AsyncExitStack()
    await exit_stack.enter_async_context(mcp_client)

    tool_registry = ToolRegistry()
    provider = ToolProviderImpl(client=mcp_client)

    await tool_registry.register_provider(provider=provider)
    tool_executor = ToolExecutor(registry=tool_registry)

    engineer_agent = EngineerAgentImpl(llm_client=llm_client)
    query_agent = QueryAgentImpl(llm_client=llm_client)
    summary_agent = SummaryAgentImpl(llm_client=llm_client)
    task_agent = TaskAgentImpl(llm_client=llm_client)

    summarize_agent_service = SummarizeAgentService(
        agent=summary_agent,
        conversation_repository=conversation_repository,
    )
    query_agent_service = QueryAgentService(
        agent=query_agent,
        summarize_agent_service=summarize_agent_service,
        conversation_repository=conversation_repository,
        tool_executor=tool_executor,
        tool_registry=tool_registry,
    )
    analyze_task_service = AnalyzeTaskService(
        agent=task_agent,
        policy=TaskAnalysisPolicy(),
        query_agent_service=query_agent_service,
        conversation_repository=conversation_repository,
    )
    task_agent_service = TaskAgentService(
        analyze_task_service=analyze_task_service,
        query_agent_service=query_agent_service,
        summarize_agent_service=summarize_agent_service,
        conversation_repository=conversation_repository,
    )
    engineer_agent_service = EngineerAgentService(
        agent=engineer_agent,
        query_agent_service=query_agent_service,
        conversation_repository=conversation_repository,
        task_agent_service=task_agent_service,
    )

    try:
        while True:
            try:
                should_exit, request = await user_request(session)
            except ValueError as e:
                logger.warn(f"Invalid prompt: {e}")
                continue
            if should_exit:
                logger.info(request.value, "dim")
                break
            try:
                conversation.start_interaction(request)
                response = await engineer_agent_service.run(conversation.id)
                conversation.stop_interaction(response)
                console.print(f"\nAgent:\t{response.content}\n")
            except KeyboardInterrupt:
                logger.warn("Request interrupted.")
            except Exception as exc:
                logger.error(f"Failed to process the request. {exc}")

    except KeyboardInterrupt:
        pass
    finally:
        await exit_stack.aclose()


def cli() -> None:
    asyncio.run(main())
