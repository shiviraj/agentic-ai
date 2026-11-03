import os
from pathlib import Path
from ollama import Client
from prompt_toolkit import PromptSession

from agent.application.services.analyze_requirement_service import AnalyzeRequirementService
from agent.application.services.create_proposal_service import CreateProposalService
from agent.application.services.discover_context_service import DiscoverContextService
from agent.application.services.execute_plan import ExecutePlan
from agent.application.services.tool_executor import ToolExecutor
from agent.application.workflow.create_plan_workflow import CreatePlanWorkflow
from agent.application.workflow.execute_plan_workflow import ExecutePlanWorkflow
from agent.application.workflow.progress_prompt_workflow import ProcessPromptWorkflow
from agent.domain.policy.context_discover_policy import ContextDiscoverPolicy
from agent.domain.policy.requirement_analysis_policy import RequirementAnalysisPolicy
from agent.domain.policy.tool_approval_policy import ToolApprovalPolicy
from agent.infrastructure.cli_approval_gateway import CliApprovalGateway
from agent.infrastructure.create_tool_registry import create_tool_registry
from agent.infrastructure.port.context_discoverer_impl import ContextDiscovererImpl
from agent.infrastructure.port.proposal_creator_impl import ProposalCreatorImpl
from agent.infrastructure.port.requirement_analyzer_impl import RequirementAnalyzerImpl
from agent.infrastructure.prompt import PROMPT_INSTRUCTIONS
from agent.infrastructure.tool_step_executor import ToolStepExecutor
from agent.interface.cli.prompt_input import create_prompt_session, user_prompt
from agent.shared.logger.Logger import Logger


def main() -> None:
    client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), timeout=180)
    model = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    logger = Logger("Main")
    registry = create_tool_registry(Path('workspace'))

    tool_executor = ToolExecutor(ToolApprovalPolicy(), CliApprovalGateway())

    step_executor = ToolStepExecutor(client, model, registry)
    requirement_analyzer = RequirementAnalyzerImpl(client=client, model=model)
    context_discoverer = ContextDiscovererImpl(client=client, model=model, tool_registry=registry)
    proposal_creator = ProposalCreatorImpl(client=client, model=model)

    requirement_analysis_policy = RequirementAnalysisPolicy()
    context_discover_policy = ContextDiscoverPolicy()

    analyze_requirement_service = AnalyzeRequirementService(requirement_analyzer, requirement_analysis_policy)
    discover_context_service = DiscoverContextService(context_discoverer, context_discover_policy, tool_executor)
    create_proposal_service = CreateProposalService(proposal_creator)

    execute_plan = ExecutePlan(step_executor, tool_executor)

    create_plan_workflow = CreatePlanWorkflow(
        analyze_requirement_service,
        discover_context_service,
        create_proposal_service
    )
    execute_plan_workflow = ExecutePlanWorkflow(execute_plan)
    workflow = ProcessPromptWorkflow(create_plan_workflow, execute_plan_workflow)

    session: PromptSession[str] = create_prompt_session()
    logger.info(PROMPT_INSTRUCTIONS, "cyan")

    try:
        while True:
            should_exit, prompt = user_prompt(session)
            if should_exit:
                logger.info(prompt.value, "dim")
                break
            if not prompt:
                continue
            try:
                workflow.execute(prompt)
            except KeyboardInterrupt:
                logger.info("Request interrupted.", 'yellow')
            except Exception as exc:
                logger.info(f"Failed to process the request. {exc}", "bold red")

    except KeyboardInterrupt:
        pass
