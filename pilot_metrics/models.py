
from pydantic import BaseModel, Field, RootModel


class LanguageMetrics(BaseModel):
    name: str
    total_engaged_users: int = 0
    total_code_acceptances: int = 0
    total_code_suggestions: int = 0
    total_code_lines_accepted: int = 0
    total_code_lines_suggested: int = 0


class ChatModel(BaseModel):
    name: str
    is_custom_model: bool
    total_chats: int = 0
    total_engaged_users: int = 0
    total_chat_copy_events: int | None = 0
    total_chat_insertion_events: int | None = 0


class PRSummaryModel(BaseModel):
    name: str
    is_custom_model: bool
    total_engaged_users: int = 0
    total_pr_summaries_created: int = 0


class RepositoryPR(BaseModel):
    name: str
    models: list[PRSummaryModel]
    total_engaged_users: int = 0


class CompletionModel(BaseModel):
    name: str
    languages: list[LanguageMetrics]
    is_custom_model: bool
    total_engaged_users: int = 0


class EditorChat(BaseModel):
    name: str
    models: list[ChatModel]
    total_engaged_users: int = 0


class CompletionEditor(BaseModel):
    name: str
    models: list[CompletionModel]
    total_engaged_users: int = 0


class CopilotIdeChat(BaseModel):
    editors: list[EditorChat] = Field(default_factory=list)
    total_engaged_users: int = 0


class CopilotDotComChat(BaseModel):
    models: list[ChatModel] = Field(default_factory=list)
    total_engaged_users: int = 0


class CopilotDotComPullRequests(BaseModel):
    repositories: list[RepositoryPR] = Field(default_factory=list)
    total_engaged_users: int = 0


class CopilotIdeCodeCompletions(BaseModel):
    editors: list[CompletionEditor] = Field(default_factory=list)
    languages: list[dict]
    total_engaged_users: int = 0


class DailyCopilotStats(BaseModel):
    date: str
    copilot_ide_chat: CopilotIdeChat
    total_active_users: int
    copilot_dotcom_chat: CopilotDotComChat
    total_engaged_users: int
    copilot_dotcom_pull_requests: CopilotDotComPullRequests
    copilot_ide_code_completions: CopilotIdeCodeCompletions


class CopilotData(RootModel[list[DailyCopilotStats]]):
    root: list[DailyCopilotStats]
