import asyncio
import os
import pathlib
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from fastmcp import Client as MCPClient
from ollama import Client as OllamaClient
from prompt_toolkit import PromptSession
from rich.console import Console

from agent.application.service.analysis_service import AnalysisService
from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.service.decomposition_service import DecompositionService
from agent.application.service.engineer_service import EngineerService
from agent.application.service.execution.code_review_execution import CodeReviewExecution
from agent.application.service.execution.execution_registry import ExecutionRegistry
from agent.application.service.execution.implementation_execution import ImplementationExecution
from agent.application.service.execution.test_design_execution import TestDesignExecution
from agent.application.service.execution.test_verification_execution import TestVerificationExecution
from agent.application.service.investigation_service import InvestigationService
from agent.application.service.response_service import ResponseService
from agent.application.service.subtask_planning_service import SubtaskPlanningService
from agent.application.service.tool_executor import ToolExecutor
from agent.application.workflow.conversation.conversation_workflow import ConversationWorkflow
from agent.application.workflow.engineer.engineer_workflow import EngineerWorkflow
from agent.application.workflow.query.query_workflow import QueryWorkflow
from agent.application.workflow.subtask.subtask_workflow import SubtaskWorkflow
from agent.application.workflow.task.task_workflow import TaskWorkflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_registry import WorkflowRegistry
from agent.domain.tool.tool_registry import ToolRegistry
from agent.infrastructure.agent.agent_impl import AgentImpl
from agent.infrastructure.agent.parser.analysis_result_parser import AnalysisResultParser
from agent.infrastructure.agent.parser.default_parser import DefaultParser
from agent.infrastructure.agent.parser.engineer_agent_result_parser import EngineerAgentResultParser
from agent.infrastructure.agent.parser.execution_plan_parser import ExecutionPlanParser
from agent.infrastructure.agent.parser.task_parser import TaskParser
from agent.infrastructure.llm.llm_client import LLMClient
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
    llm_client = LLMClient(client=ollama_client, model=model)

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
        agent=AgentImpl(llm_client, "investigation_agent", DefaultParser()),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
    )
    response_service = ResponseService(
        agent=AgentImpl(llm_client, "response_agent", DefaultParser()),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
    )
    engineer_service = EngineerService(
        agent=AgentImpl(llm_client, "engineer_agent", EngineerAgentResultParser()),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
    )
    analysis_service = AnalysisService(
        agent=AgentImpl(llm_client, "analysis_agent", AnalysisResultParser()),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
        investigation_service=investigation_service,
    )
    decomposition_service = DecompositionService(
        agent=AgentImpl(llm_client, "decomposition_agent", TaskParser()),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
    )

    execution_workflow = SubtaskWorkflow(
        subtask_planning_service=SubtaskPlanningService(
            agent=AgentImpl(llm_client, "subtask_planning_agent", ExecutionPlanParser()),
            conversation_service=conversation_service,
            conversation_context_service=conversation_context_service,
        ),
        execution_registry=ExecutionRegistry(
            code_review_execution=CodeReviewExecution(
                agent=AgentImpl(llm_client, "code_review_agent", DefaultParser()),
                conversation_service=conversation_service,
                conversation_context_service=conversation_context_service,
                tool_executor=tool_executor,
                tool_registry=tool_registry,
            ),
            implementation_execution=ImplementationExecution(
                agent=AgentImpl(llm_client, "implementation_agent", DefaultParser()),
                conversation_service=conversation_service,
                conversation_context_service=conversation_context_service,
                tool_executor=tool_executor,
                tool_registry=tool_registry,
            ),
            test_design_execution=TestDesignExecution(
                agent=AgentImpl(llm_client, "test_design_agent", DefaultParser()),
                conversation_service=conversation_service,
                conversation_context_service=conversation_context_service,
                tool_executor=tool_executor,
                tool_registry=tool_registry,
            ),
            test_verification_execution=TestVerificationExecution(
                agent=AgentImpl(llm_client, "test_verification_agent", DefaultParser()),
                conversation_service=conversation_service,
                conversation_context_service=conversation_context_service,
                tool_executor=tool_executor,
                tool_registry=tool_registry,
            ),
        ),
    )

    workflow_registry = WorkflowRegistry(
        conversation_workflow=ConversationWorkflow(),
        query_workflow=QueryWorkflow(investigation_service=investigation_service),
        task_workflow=TaskWorkflow(
            analysis_service=analysis_service,
            decomposition_service=decomposition_service,
            subtask_workflow=execution_workflow,
        ),
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
