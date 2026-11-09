import json

from agent.domain.task.task import Task
from agent.domain.task.task_id import TaskId
from agent.domain.task.task_status import TaskStatus
from agent.infrastructure.agents.task_analyser_agent import TaskAnalyserAgent

from agent.application.port.llm_client import LLMClient
from agent.domain.agent.agent_result import ResultStatus
from agent.domain.agent.agent_role import AgentRole
from agent.domain.errors import LlmUnavailableError
from agent.domain.llm.message import Role
from tests.fakes.fake_llm_client import FakeLLMClient


def reply(ready, requirements="", questions=()):
    return json.dumps({"ready": ready, "requirements": requirements, "questions": list(questions)})


def make_task() -> Task:
    return Task(id=TaskId.generate(), prompt="implement healthcheck endpoint")


def test_role_is_analyser():
    assert TaskAnalyserAgent(FakeLLMClient([])).role == AgentRole.ANALYSER


def test_clear_task_returns_done_with_requirements():
    llm = FakeLLMClient([reply(True, "- GET /healthcheck returns 200")])
    result = TaskAnalyserAgent(llm).run(make_task())

    assert result.status == ResultStatus.DONE
    assert result.output == "- GET /healthcheck returns 200"
    assert llm.json_modes == [True]


def test_unclear_task_returns_questions():
    llm = FakeLLMClient([reply(False, questions=["Which framework?", "Which port?"])])
    result = TaskAnalyserAgent(llm).run(make_task())

    assert result.status == ResultStatus.NEEDS_CLARIFICATION
    assert result.questions == ("Which framework?", "Which port?")


def test_only_first_three_questions_are_kept():
    llm = FakeLLMClient([reply(False, questions=["1", "2", "3", "4", "5"])])
    result = TaskAnalyserAgent(llm).run(make_task())
    assert result.questions == ("1", "2", "3")


def test_prompt_contains_task_and_earlier_answers():
    llm = FakeLLMClient([reply(True, "ok")])
    task = make_task()
    task.add_clarification("Which framework?", "Express")

    TaskAnalyserAgent(llm).run(task)

    system, user = llm.calls[0]
    assert system.role == Role.SYSTEM
    assert "Task Analyser" in system.content
    assert "implement healthcheck endpoint" in user.content
    assert "Which framework?" in user.content
    assert "Express" in user.content


def test_bad_answer_is_retried_with_feedback():
    llm = FakeLLMClient(["this is not json", reply(True, "- fixed")])
    result = TaskAnalyserAgent(llm).run(make_task())

    assert result.status == ResultStatus.DONE
    assert len(llm.calls) == 2
    second_call = llm.calls[1]
    assert len(second_call) == 4  # system, user, bad assistant reply, correction
    assert second_call[2].role == Role.ASSISTANT
    assert "not valid" in second_call[3].content


def test_two_bad_answers_give_failed_result():
    llm = FakeLLMClient(["nope", "still nope"])
    result = TaskAnalyserAgent(llm).run(make_task())

    assert result.status == ResultStatus.FAILED
    assert len(llm.calls) == 2


def test_ready_with_empty_requirements_is_rejected():
    llm = FakeLLMClient([reply(True, ""), reply(True, "")])
    assert TaskAnalyserAgent(llm).run(make_task()).status == ResultStatus.FAILED


def test_not_ready_without_questions_is_rejected():
    llm = FakeLLMClient([reply(False), reply(False)])
    assert TaskAnalyserAgent(llm).run(make_task()).status == ResultStatus.FAILED


def test_llm_outage_gives_failed_result():
    class DownLlm(LLMClient):
        def chat(self, messages, json_mode=False):
            raise LlmUnavailableError("server down")

    result = TaskAnalyserAgent(DownLlm()).run(make_task())
    assert result.status == ResultStatus.FAILED
    assert "server down" in result.output


def test_agent_does_not_change_the_task():
    llm = FakeLLMClient([reply(True, "- something")])
    task = make_task()
    TaskAnalyserAgent(llm).run(task)

    assert task.status == TaskStatus.ANALYSING
    assert task.requirements is None
