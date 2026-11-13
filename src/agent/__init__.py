import asyncio
import os

from dotenv import load_dotenv
from ollama import Client as OllamaClient
from prompt_toolkit import PromptSession
from rich.console import Console

from agent.application.service.conversation_context_service import ConversationContextService
from agent.application.service.conversation_service import ConversationService
from agent.application.workflow.engineer.engineer_workflow import EngineerWorkflow
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.aggregate.conversation import Conversation
from agent.infrastructure.agents.engineer_agent_impl import EngineerAgentImpl
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl
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

    # mcp_client = MCPClient(pathlib.Path("src/agent/infrastructure/mcp/server/filesystem_server.py"))
    # exit_stack = AsyncExitStack()
    # await exit_stack.enter_async_context(mcp_client)

    # tool_registry = ToolRegistry()
    # provider = ToolProviderImpl(client=mcp_client)

    # await tool_registry.register_provider(provider=provider)
    # tool_executor = ToolExecutor(registry=tool_registry)

    # engineer_agent = EngineerAgentImpl(llm_client=llm_client)
    # query_agent = QueryAgentImpl(llm_client=llm_client)
    # summary_agent = SummaryAgentImpl(llm_client=llm_client)
    # task_agent = TaskAgentImpl(llm_client=llm_client)
    # task_decomposition_agent = TaskDecompositionAgentImpl(llm_client=llm_client)
    # subtask_planning_agent = SubtaskPlanningAgentImpl(llm_client=llm_client)

    # summarize_agent_service = SummarizeAgentService(
    #     agent=summary_agent,
    #     conversation_repository=conversation_repository,
    # )
    # query_agent_service = QueryAgentService(
    #     agent=query_agent,
    #     summarize_agent_service=summarize_agent_service,
    #     conversation_repository=conversation_repository,
    #     tool_executor=tool_executor,
    #     tool_registry=tool_registry,
    # )
    # task_decomposition_service = TaskDecompositionService(
    #     agent=task_decomposition_agent,
    #     conversation_repository=conversation_repository,
    # )
    # analyze_task_service = AnalyzeTaskService(
    #     agent=task_agent,
    #     policy=TaskAnalysisPolicy(),
    #     query_agent_service=query_agent_service,
    #     conversation_repository=conversation_repository,
    # )
    # plan_subtask_service = PlanSubtaskService(
    #     agent=subtask_planning_agent,
    #     conversation_repository=conversation_repository,
    # )
    # task_agent_service = TaskAgentService(
    #     analyze_task_service=analyze_task_service,
    #     task_decomposition_service=task_decomposition_service,
    #     query_agent_service=query_agent_service,
    #     plan_subtask_service=plan_subtask_service,
    #     summarize_agent_service=summarize_agent_service,
    #     conversation_repository=conversation_repository,
    # )
    # engineer_agent_service = EngineerAgentService(
    #     agent=engineer_agent,
    #     query_agent_service=query_agent_service,
    #     conversation_repository=conversation_repository,
    #     task_agent_service=task_agent_service,
    # )

    conversation_service = ConversationService(repository=conversation_repository)
    conversation_context_service = ConversationContextService(conversation_repository=conversation_repository)

    engineer_workflow = EngineerWorkflow(
        engineer_agent=EngineerAgentImpl(llm_client=llm_client),
        conversation_service=conversation_service,
        conversation_context_service=conversation_context_service,
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
                response = engineer_workflow.execute(
                    WorkflowInput(conversation_id=conversation.id, user_request=request)
                )
                # conversation.stop_interaction(response)
                console.print(f"\nAgent:\t{response}\n")
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
