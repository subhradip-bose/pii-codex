from __future__ import annotations

from typing import List, Counter

import strawberry

from pii_codex.models.common import RiskLevel, RiskLevelDefinition


# PII detection, risk assessment, and analysis models


@strawberry.type
class RiskAssessment:
    pii_type_detected: str = None
    risk_level: int = RiskLevel.LEVEL_ONE.value
    risk_level_definition: str = (
        RiskLevelDefinition.LEVEL_ONE.value
    )  # Default if it's not semi or fully identifiable
    cluster_membership_type: str = None
    hipaa_category: str = None
    dhs_category: str = None
    nist_category: str = None


@strawberry.type
class RiskAssessmentList:
    risk_assessments: List[RiskAssessment]
    average_risk_score: float


@strawberry.type
class DetectionResult:
    """
    Type associated with a singular PII detection (e.g. detection of an email in a string), its associated risk score,
    and where it is located in a string.
    """

    entity_type: str
    score: float
    start: int
    end: int


@strawberry.type
class AnalysisResultItem:
    """
    The results associated to a single detection of a single string (e.g. Social Media Post, SMS, etc.)
    """

    detection: DetectionResult
    risk_assessment: RiskAssessment

    def to_dict(self):
        return {
            "riskAssessment": self.risk_assessment.__dict__,
            "detection": self.detection.__dict__,
        }

    def to_flattened_dict(self):
        assessment = self.risk_assessment.__dict__.copy()
        assessment.update(self.detection.__dict__)
        return assessment


@strawberry.type
class AnalysisResult:
    """
    The analysis results associated with several detections within a single string (e.g. Social Media Post, SMS, etc.)
    """

    index: int = 0
    analysis: List[AnalysisResultItem]
    mean_risk_score: float = 0.0

    def to_dict(self):
        return {
            "analysis": [item.to_flattened_dict() for item in self.analysis],
            "index": self.index,
            "mean_risk_score": self.mean_risk_score,
        }

    def get_detected_types(self) -> List[str]:
        return [pii.detection.entity_type for pii in self.analysis]


@strawberry.type
class AnalysisResultSet:
    """
    The analysis results associated with a collection of strings or documents (e.g. Social Media Posts, forum thread,
    etc.). Includes most/least detected PII types within the collection, average risk score of analyses,
    """

    analyses: List[AnalysisResult]
    detection_count: int = 0
    detected_pii_types: List[str] = None
    detected_pii_type_frequencies: Counter = (
        None  # Frequency count of PII types detected in entire collection
    )
    risk_scores: List[float] = None
    mean_risk_score: float = 1.0  # Default is 1 for non-identifiable
    risk_score_standard_deviation: float = 0.0
    risk_score_variance: float = 0.0
    collection_name: str = None  # Optional ability for analysts to name a set (see analysis storage step in notebooks)

    def to_dict(self):
        return {
            "collection_name": self.collection_name,
            "analyses": [item.to_dict() for item in self.analyses],
            "detection_count": self.detection_count,
            "mean_risk_score": self.mean_risk_score,
            "risk_scores": self.risk_scores,
            "risk_score_standard_deviation": self.risk_score_standard_deviation,
            "risk_score_variance": self.risk_score_variance,
            "detected_pii_types": self.detected_pii_types,
            "detected_pii_type_frequencies": dict(self.detected_pii_type_frequencies),
        }
