"""Shared LangGraph agent used by all three platform notebooks.

The same `build_agent()` factory is imported by 01_langfuse, 02_langsmith,
and 03_galileo — that way each platform traces an identical workflow.

Scenario: a permission-checking agent with three dependent tools.

    get_ads_id(employee_name)            -> ads_id
    get_permissions(ads_id)              -> list[str]
    check_admin_access(permissions, resource) -> bool

Each tool's output feeds the next, so the number of tool calls the LLM
makes depends on what the user actually asks for:

    "What's the ads_id for X?"             -> 1 tool
    "What permissions does X have?"        -> 2 tools
    "Does X have admin on resource R?"     -> 3 tools
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


# ---------------------------------------------------------------------------
# Fake corporate directory — deterministic so traces are easy to compare
# ---------------------------------------------------------------------------

EMPLOYEES: dict[str, str] = {
    "jane doe": "ADS-1001",
    "john smith": "ADS-1002",
    "alice nguyen": "ADS-1003",
    "bob carter": "ADS-1004",
}

PERMISSIONS: dict[str, list[str]] = {
    "ADS-1001": ["read:billing-prod", "admin:billing-prod", "read:analytics"],
    "ADS-1002": ["read:analytics"],
    "ADS-1003": ["read:billing-prod", "read:analytics", "admin:analytics"],
    "ADS-1004": [],
}

# Lightweight HR/profile data — keyed by ads_id. This is what the agent
# needs when asked to judge whether someone's access matches their role.
PROFILES: dict[str, dict] = {
    "ADS-1001": {
        "full_name": "Jane Doe",
        "role": "Senior Billing Engineer",
        "team": "Billing Platform",
        "manager": "Aaron Williams",
        "tenure_years": 4.2,
        "last_review_status": "Meets expectations",
    },
    "ADS-1002": {
        "full_name": "John Smith",
        "role": "Frontend Engineer",
        "team": "Web Platform",
        "manager": "Aaron Williams",
        "tenure_years": 0.7,
        "last_review_status": "On track",
    },
    "ADS-1003": {
        "full_name": "Alice Nguyen",
        "role": "Data Analyst",
        "team": "Analytics",
        "manager": "Maria Lopez",
        "tenure_years": 1.5,
        "last_review_status": "Exceeds expectations",
    },
    "ADS-1004": {
        "full_name": "Bob Carter",
        "role": "Operations Intern",
        "team": "Operations",
        "manager": "Alice Nguyen",
        "tenure_years": 0.3,
        "last_review_status": None,
    },
}


# ---------------------------------------------------------------------------
# Tools — plain @tool functions so every observability SDK can intercept them
# ---------------------------------------------------------------------------

@tool
def get_ads_id(employee_name: str) -> str:
    """Look up an employee's internal ads_id by their full name.

    Args:
        employee_name: The employee's full name, e.g. "Jane Doe".

    Returns:
        The ads_id string (e.g. "ADS-1001"), or an error message if unknown.
    """
    key = employee_name.strip().lower()
    if key not in EMPLOYEES:
        return f"ERROR: no employee found with name '{employee_name}'"
    return EMPLOYEES[key]


@tool
def get_permissions(ads_id: str) -> list[str]:
    """Fetch the list of permission strings for a given ads_id.

    Args:
        ads_id: The internal ads_id returned by get_ads_id.

    Returns:
        A list of permission strings like "read:billing-prod" or
        "admin:analytics". Empty list if the user has no permissions.
    """
    key = ads_id.strip().upper()
    if key not in PERMISSIONS:
        return [f"ERROR: unknown ads_id '{ads_id}'"]
    return PERMISSIONS[key]


@tool
def check_admin_access(permissions: list[str], resource: str) -> bool:
    """Return True iff `permissions` grants admin access to `resource`.

    Args:
        permissions: The list returned by get_permissions.
        resource: Resource name to check (e.g. "billing-prod").

    Returns:
        True if "admin:<resource>" is in the permission list, else False.
    """
    needle = f"admin:{resource.strip()}"
    return needle in permissions


@tool
def get_employee_profile(ads_id: str) -> dict:
    """Fetch HR/profile context for an employee: role, team, manager, tenure,
    and most-recent review status. Use this when the user asks for context
    about who someone is, or when judging whether their access matches
    their role.

    Args:
        ads_id: The internal ads_id returned by get_ads_id.

    Returns:
        A dict with keys: full_name, role, team, manager, tenure_years,
        last_review_status. Returns {"error": "..."} for unknown ads_ids.
    """
    key = ads_id.strip().upper()
    if key not in PROFILES:
        return {"error": f"unknown ads_id '{ads_id}'"}
    return PROFILES[key]


TOOLS = [get_ads_id, get_permissions, check_admin_access, get_employee_profile]


# ---------------------------------------------------------------------------
# Agent system prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an internal IT helpdesk agent. You help staff with employee identity,
permissions, role context, and whether someone's access is appropriate for
their role.

You have four tools available:

  1. get_ads_id(employee_name) -> ads_id
  2. get_permissions(ads_id)   -> list of permission strings
  3. check_admin_access(permissions, resource) -> bool
  4. get_employee_profile(ads_id) -> {full_name, role, team, manager,
     tenure_years, last_review_status}

Tool selection — use only what's needed:
  - Ads ID lookup only -> get_ads_id, stop.
  - Permission list -> get_ads_id then get_permissions, stop.
  - Admin access on a specific resource -> get_ads_id, get_permissions,
    check_admin_access.
  - Role / team / manager / tenure context -> get_ads_id then
    get_employee_profile.
  - Summarize, explain, or analyze whether someone's access is appropriate
    for their role -> get_ads_id, get_employee_profile, get_permissions,
    and check_admin_access as needed (all four tools).

When the user asks for analysis, a summary, or whether access is
appropriate, you SHOULD engage with the question:
  - Fetch the relevant data first.
  - Provide a clear, brief response that includes BOTH the facts AND your
    analysis of whether the access aligns with their role.
  - You can and should share an opinion grounded in the data
    (e.g. "admin on billing-prod is consistent with a Senior Billing
    Engineer role"). You may note that final policy decisions belong to
    managers or security review, but do NOT refuse to provide analysis.

Call exactly one tool at a time, wait for the result, then decide what
to do next. After the final tool result, summarise for the user in
1-3 short sentences.
"""


# ---------------------------------------------------------------------------
# Fixture scenarios — each pinned to a specific tool-call depth
# ---------------------------------------------------------------------------

SCENARIOS: list[dict] = [
    {
        "id": "one_tool",
        "expected_tool_calls": 1,
        "prompt": "What's the ads_id for Jane Doe?",
        "expected_answer": "ADS-1001",                  # exact match check works here
        "llm_judge_fit": False,                          # closed factual answer; deterministic check is better
    },
    {
        "id": "two_tools",
        "expected_tool_calls": 2,
        "prompt": "What permissions does Alice Nguyen currently have?",
        "expected_answer": ["read:billing-prod", "read:analytics", "admin:analytics"],
        "llm_judge_fit": False,
    },
    {
        "id": "three_tools",
        "expected_tool_calls": 3,
        "prompt": "Does Jane Doe have admin access to billing-prod?",
        "expected_answer": True,
        "llm_judge_fit": False,
    },
    {
        # Open-ended judgment scenario. Uses all four tools: ads_id ->
        # profile (role/team) -> permissions -> admin check. The *quality*
        # of the answer (clarity, completeness, reasoned judgment) is
        # fuzzy — there's no single correct response, which makes this a
        # natural fit for LLM-as-judge evaluation.
        "id": "judgment_call",
        "expected_tool_calls": 4,
        "prompt": (
            "Briefly explain who Jane Doe is, what she has access to, "
            "and whether she should keep her admin rights."
        ),
        "expected_answer": None,                         # no single correct answer
        "rubric": (
            "Answer should: (1) identify Jane Doe by role/team (from "
            "get_employee_profile), (2) summarize her permissions, "
            "(3) explicitly call out admin:billing-prod, (4) make a "
            "reasoned judgment about whether the admin access is "
            "appropriate given her role (a Senior Billing Engineer "
            "having admin on billing-prod is consistent), and (5) stay "
            "concise (~3 sentences)."
        ),
        "llm_judge_fit": True,
    },
    {
        # Tier 1 — error path. The agent asks about a non-existent
        # employee; get_ads_id returns an ERROR string. Demonstrates how
        # each platform renders tool errors and how the agent recovers.
        "id": "error_path",
        "expected_tool_calls": 1,
        "prompt": "What's the ads_id for Nobody McNobody?",
        "expected_answer": None,
        "rubric": "Agent should acknowledge the employee was not found rather than fabricating an answer.",
        "llm_judge_fit": False,
    },
]

DATASET_NAME = "permission-agent-scenarios"

# ---------------------------------------------------------------------------
# Tier 1 scenarios that aren't standard one-shot prompts
# ---------------------------------------------------------------------------

# Multi-turn conversation — three turns sharing one session_id.
# Each turn builds on the previous; the agent should reuse context from
# tool results in earlier turns instead of re-fetching.
MULTI_TURN_CONVERSATION: list[str] = [
    "Tell me about Jane Doe — who is she at the company?",
    "What kind of access does she currently have?",
    "Given her role, is it appropriate for her to have admin on billing-prod?",
]


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


PROMPT_NAME = "permission-agent-system"


def fetch_system_prompt(source: str = "local") -> str:
    """Fetch the system prompt from a platform's prompt registry.

    Args:
        source: where to pull from. One of:
            "local"     — return the SYSTEM_PROMPT constant (no network call)
            "langfuse"  — pull from Langfuse Prompts
            "langsmith" — pull from LangSmith Prompt Hub
            "galileo"   — pull from Galileo project templates

    Returns:
        The system prompt string. Falls back to the local constant if the
        registry lookup fails (with a printed warning) so notebooks still
        run when a platform is misconfigured.
    """
    if source == "local":
        return SYSTEM_PROMPT

    try:
        if source == "langfuse":
            from langfuse import Langfuse
            lf = Langfuse()
            p = lf.get_prompt(PROMPT_NAME, label="production")
            return p.prompt

        if source == "langsmith":
            from langsmith import Client
            client = Client()
            template = client.pull_prompt(PROMPT_NAME)
            # template is a ChatPromptTemplate — extract the system message
            for msg in template.messages:
                # First message that has a system-like role
                tmpl = getattr(msg, "prompt", None)
                content = getattr(tmpl, "template", None) if tmpl else None
                role = getattr(msg, "role", "") or ""
                if "system" in str(type(msg)).lower() or role == "system":
                    return content or msg.format().content
            # Fallback: just take the first message's template
            first = template.messages[0]
            return getattr(getattr(first, "prompt", None), "template", SYSTEM_PROMPT)

        if source == "galileo":
            from galileo.prompts import get_prompt
            import os
            import json as _json
            t = get_prompt(name=PROMPT_NAME, project_name=os.environ.get("GALILEO_PROJECT", "observability-comparison"))
            # `version.template` comes back from the API as a JSON string
            # holding a list of message dicts: [{"role": "system", "content": "..."}, ...]
            version = getattr(t, "selected_version", None) or getattr(t, "version", None)
            raw_template = getattr(version, "template", None) if version else None
            if isinstance(raw_template, str):
                try:
                    messages = _json.loads(raw_template)
                except Exception:
                    messages = []
            elif isinstance(raw_template, list):
                messages = raw_template
            else:
                messages = []
            for m in messages:
                role = m.get("role") if isinstance(m, dict) else getattr(m, "role", "")
                if str(role).lower().endswith("system"):
                    content = m.get("content") if isinstance(m, dict) else getattr(m, "content", None)
                    if isinstance(content, str):
                        return content
                    if isinstance(content, list):
                        return "".join(
                            (p.get("text") if isinstance(p, dict) else getattr(p, "text", str(p)))
                            for p in content
                        )
            return SYSTEM_PROMPT
    except Exception as e:
        print(f"  [fetch_system_prompt] {source} lookup failed ({type(e).__name__}: {e}); falling back to local SYSTEM_PROMPT")
        return SYSTEM_PROMPT

    raise ValueError(f"Unknown prompt source: {source!r}")


def build_agent(
    model: str = "claude-sonnet-4-6",
    temperature: float = 0.0,
    prompt_source: str = "local",
    custom_system_prompt: str | None = None,
):
    """Build and compile the LangGraph ReAct agent.

    The graph shape is:

        START -> agent -> tools -> agent -> ... -> END

    The conditional edge after `agent` routes to `tools` whenever the last
    AIMessage contains tool_calls, otherwise to END.

    Args:
        model: Anthropic model id
        temperature: sampling temperature
        prompt_source: where to fetch the system prompt — "local",
            "langfuse", "langsmith", or "galileo". See fetch_system_prompt.
        custom_system_prompt: if provided, this string is used as the
            system prompt and `prompt_source` is ignored. Used by the
            hallucination scenario to swap in a loosened prompt without
            touching the production registry.
    """
    system_prompt = custom_system_prompt if custom_system_prompt is not None else fetch_system_prompt(prompt_source)

    llm = ChatAnthropic(model=model, temperature=temperature)
    llm_with_tools = llm.bind_tools(TOOLS)

    def agent_node(state: AgentState) -> dict:
        messages = state["messages"]
        # Prepend the system prompt if the first message isn't already one.
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt), *messages]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()
