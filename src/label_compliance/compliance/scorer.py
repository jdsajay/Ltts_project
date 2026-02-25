"""
Compliance Scorer
==================
Aggregates individual rule match results into an overall
compliance score for a label, with severity-weighted scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from label_compliance.compliance.matcher import MatchResult
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# Severity weights for scoring
SEVERITY_WEIGHTS = {
    "critical": 3.0,
    "major": 2.0,
    "minor": 1.0,
}


@dataclass
class ComplianceScore:
    """Overall compliance assessment for a label."""

    label_name: str
    total_rules: int = 0
    passed: int = 0
    partial: int = 0
    failed: int = 0
    score_pct: float = 0.0  # 0-100%
    weighted_score: float = 0.0
    status: str = "UNKNOWN"  # "COMPLIANT", "PARTIAL", "NON-COMPLIANT"
    results: list[MatchResult] = field(default_factory=list)
    critical_gaps: list[MatchResult] = field(default_factory=list)
    new_2024_gaps: list[MatchResult] = field(default_factory=list)
    spec_violation_count: int = 0
    rules_with_spec_failures: int = 0

    @property
    def gap_count(self) -> int:
        return self.failed + self.partial

    @property
    def critical_count(self) -> int:
        return len(self.critical_gaps)


def compute_score(
    label_name: str,
    match_results: list[MatchResult],
    compliant_threshold: float = 0.85,
    partial_threshold: float = 0.50,
) -> ComplianceScore:
    """
    Compute overall compliance score for a label.

    Scoring:
    - Each rule gets PASS=1, PARTIAL=0.5, FAIL=0
    - Weighted by severity (critical=3x, major=2x, minor=1x)
    - Overall status based on thresholds
    """
    if not match_results:
        return ComplianceScore(label_name=label_name, status="UNKNOWN")

    total_weight = 0.0
    earned_weight = 0.0
    passed = 0
    partial = 0
    failed = 0
    critical_gaps = []
    new_2024_gaps = []
    spec_violation_count = 0
    rules_with_spec_failures = 0

    for result in match_results:
        weight = SEVERITY_WEIGHTS.get(result.severity, 1.0)
        total_weight += weight

        if result.status == "PASS":
            earned_weight += weight
            passed += 1
        elif result.status == "PARTIAL":
            earned_weight += weight * 0.5
            partial += 1
        else:
            failed += 1

        # Track critical and new-2024 gaps
        if result.status in ("FAIL", "PARTIAL") and result.severity == "critical":
            critical_gaps.append(result)
        if result.status in ("FAIL", "PARTIAL") and result.new_in_2024:
            new_2024_gaps.append(result)

        # Track spec violations
        if result.spec_violations:
            spec_violation_count += len(result.spec_violations)
            rules_with_spec_failures += 1
            # Apply additional penalty for spec violations
            # Each spec violation reduces earned weight for this rule
            spec_penalty = min(
                len(result.spec_violations) * 0.1 * weight,
                weight * 0.3,  # cap penalty at 30% of rule weight
            )
            earned_weight = max(0, earned_weight - spec_penalty)

    score_pct = (earned_weight / max(total_weight, 1)) * 100
    weighted = earned_weight / max(total_weight, 1)

    # Spec failures can prevent COMPLIANT status even if text matches are good
    if weighted >= compliant_threshold and not critical_gaps and rules_with_spec_failures == 0:
        status = "COMPLIANT"
    elif weighted >= compliant_threshold and not critical_gaps:
        status = "PARTIAL"  # text passes but specs have issues
    elif weighted >= partial_threshold:
        status = "PARTIAL"
    else:
        status = "NON-COMPLIANT"

    score = ComplianceScore(
        label_name=label_name,
        total_rules=len(match_results),
        passed=passed,
        partial=partial,
        failed=failed,
        score_pct=round(score_pct, 1),
        weighted_score=round(weighted, 4),
        status=status,
        results=match_results,
        critical_gaps=critical_gaps,
        new_2024_gaps=new_2024_gaps,
        spec_violation_count=spec_violation_count,
        rules_with_spec_failures=rules_with_spec_failures,
    )

    logger.info(
        "Score: %s → %s (%.1f%%) — %d PASS, %d PARTIAL, %d FAIL, "
        "%d critical gaps, %d spec violations across %d rules",
        label_name, status, score_pct, passed, partial, failed,
        len(critical_gaps), spec_violation_count, rules_with_spec_failures,
    )
    return score
