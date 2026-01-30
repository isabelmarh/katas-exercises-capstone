from enum import Enum
from pydantic import BaseModel, Field, computed_field


class QualityLevel(str, Enum):
    EXCELLENT = "excellent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FAIL = "fail"

    @property
    def points(self) -> int:
        return {
            QualityLevel.EXCELLENT: 100,
            QualityLevel.HIGH: 80,
            QualityLevel.MEDIUM: 60,
            QualityLevel.LOW: 40,
            QualityLevel.FAIL: 20,
        }[self]

    @property
    def color(self) -> str:
        return {
            QualityLevel.EXCELLENT: "#00CC66",
            QualityLevel.HIGH: "#00B050",
            QualityLevel.MEDIUM: "#F7B500",
            QualityLevel.LOW: "#FF9933",
            QualityLevel.FAIL: "#F2617A",
        }[self]

    @classmethod
    def from_score(cls, score: int) -> "QualityLevel":
        if score >= 90:
            return cls.EXCELLENT
        elif score >= 75:
            return cls.HIGH
        elif score >= 60:
            return cls.MEDIUM
        elif score >= 40:
            return cls.LOW
        else:
            return cls.FAIL


class CategoryAssessment(BaseModel):
    quality: QualityLevel
    justification: str = Field(min_length=50)
    areas_for_improvement: list[str] = Field(min_length=2)


class SystemArchitectureAssessment(CategoryAssessment):
    category: str = Field(default="System Architecture & Design")


class ImplementationAssessment(CategoryAssessment):
    category: str = Field(default="Implementation & Functionality")


class EvaluationAssessment(CategoryAssessment):
    category: str = Field(default="Evaluation & Metrics")


class CodeQualityAssessment(CategoryAssessment):
    category: str = Field(default="Code Quality & Engineering Practices")


class DocumentationAssessment(CategoryAssessment):
    category: str = Field(default="Documentation & User Experience")


class InnovationAssessment(CategoryAssessment):
    category: str = Field(default="Innovation & Initiative (Bonus)")


class CapstoneAssessment(BaseModel):
    system_architecture: SystemArchitectureAssessment
    implementation: ImplementationAssessment
    evaluation: EvaluationAssessment
    code_quality: CodeQualityAssessment
    documentation: DocumentationAssessment
    innovation: InnovationAssessment
    summary: str = Field(min_length=100)
    strengths: list[str] = Field(min_length=3)
    areas_for_improvement: list[str] = Field(min_length=2)

    @computed_field
    @property
    def overall_rating(self) -> QualityLevel:
        return QualityLevel.from_score(self.overall_score)

    @computed_field
    @property
    def overall_score(self) -> int:
        scores = [
            self.system_architecture.quality.points,
            self.implementation.quality.points,
            self.evaluation.quality.points,
            self.code_quality.quality.points,
            self.documentation.quality.points,
            self.innovation.quality.points,
        ]
        return round(sum(scores) / 6)


class AgentKataAssessment(BaseModel):
    """Lightweight assessment for single-file Pydantic AI agent katas.

    Focuses on core framework usage and actionable feedback rather than scoring.
    """

    summary: str = Field(
        min_length=50,
        description="Short, friendly overview of how well the agent kata uses Pydantic AI.",
    )
    pydantic_ai_usage: str = Field(
        min_length=50,
        description="Assessment of how Pydantic AI is used (Agent, tools, output_type, etc.).",
    )
    strengths: list[str] = Field(
        min_length=2,
        description="Concrete things the kata does well.",
    )
    areas_for_improvement: list[str] = Field(
        min_length=2,
        description="Specific suggestions to improve the agent or code.",
    )
    missing_elements: list[str] = Field(
        default_factory=list,
        description="Important Pydantic AI pieces that are missing or could be added.",
    )


class MCPKataAssessment(BaseModel):
    """Lightweight assessment for single-file MCP server katas.

    Focuses on core FastMCP/MCP server usage and actionable feedback rather than scoring.
    """

    summary: str = Field(
        min_length=50,
        description="Short, friendly overview of how well the MCP server kata uses FastMCP/MCP.",
    )
    mcp_server_usage: str = Field(
        min_length=50,
        description="Assessment of how FastMCP/MCP is used (FastMCP instance, tools, prompts, resources, etc.).",
    )
    strengths: list[str] = Field(
        min_length=2,
        description="Concrete things the kata does well.",
    )
    areas_for_improvement: list[str] = Field(
        min_length=2,
        description="Specific suggestions to improve the MCP server or code.",
    )
    missing_elements: list[str] = Field(
        default_factory=list,
        description="Important MCP/FastMCP pieces that are missing or could be added (tools, prompts, resources, error handling, etc.).",
    )
