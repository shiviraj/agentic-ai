import asyncio
import os
import pathlib
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from fastmcp import Client as MCPClient
from ollama import Client as OllamaClient
from prompt_toolkit import PromptSession
from rich.console import Console

from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.service.engineer_service import EngineerService
from agent.application.service.investigation_service import InvestigationService
from agent.application.service.response_service import ResponseService
from agent.application.service.tool_executor import ToolExecutor
from agent.application.workflow.conversation.conversation_workflow import ConversationWorkflow
from agent.application.workflow.engineer.engineer_workflow import EngineerWorkflow
from agent.application.workflow.query.query_workflow import QueryWorkflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_registry import WorkflowRegistry
from agent.domain.tool.tool_registry import ToolRegistry
from agent.infrastructure.agents.conversation_agent_impl import ConversationAgentImpl
from agent.infrastructure.agents.engineer_agent_impl import EngineerAgentImpl
from agent.infrastructure.agents.investigation_agent_impl import InvestigationAgentImpl
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl
from agent.infrastructure.mcp.tool_provider_impl import ToolProviderImpl
from agent.infrastructure.persistence.conversation_repository_impl import ConversationRepositoryImpl
from agent.infrastructure.prompts.prompt_loader import load_prompt
from agent.interface.cli.user_input import create_prompt_session, user_request
from agent.shared.logger.logger import Logger


async def main() -> None:
    logger = Logger("Main")
    load_dotenv()
    model = os.getenv("MODEL") or "llama3.2:latest"
    host = os.getenv("API_URL")
    timeout = int(os.getenv("TIMEOUT", "60"))

    ollama_client = OllamaClient(host=host, timeout=timeout)
    llm_client = LLMClientImpl(client=ollama_client, model=model)

    session: PromptSession[str] = create_prompt_session()
    console = Console()
    console.print(f"[cyan]{load_prompt('instruction')}[/cyan]")

    mcp_client = MCPClient(pathlib.Path("src/agent/infrastructure/mcp/server/filesystem_server.py"))
    exit_stack = AsyncExitStack()
    await exit_stack.enter_async_context(mcp_client)

    tool_registry = ToolRegistry()
    provider = ToolProviderImpl(client=mcp_client, server_name="filesystem")

    await tool_registry.register_provider(provider=provider)
    tool_executor = ToolExecutor(registry=tool_registry)

    conversation_repository = ConversationRepositoryImpl()
    conversation_service = ConversationService(repository=conversation_repository)
    conversation_context_service = ConversationContextService(conversation_repository=conversation_repository)
    conversation = conversation_service.create()

    investigation_service = InvestigationService(
        agent=InvestigationAgentImpl(llm_client=llm_client),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
    )
    response_service = ResponseService(
        agent=ConversationAgentImpl(llm_client=llm_client),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
    )
    engineer_service = EngineerService(
        agent=EngineerAgentImpl(llm_client=llm_client),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
    )

    workflow_registry = WorkflowRegistry(
        conversation_workflow=ConversationWorkflow(),
        query_workflow=QueryWorkflow(investigation_service=investigation_service),
    )

    engineer_workflow = EngineerWorkflow(
        engineer_service=engineer_service,
        response_service=response_service,
        workflow_registry=workflow_registry,
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
                # conversation.start_interaction(request)
                response = await engineer_workflow.execute(
                    WorkflowInput(conversation_id=conversation.id, user_request=request)
                )
                # conversation.stop_interaction(response)
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
