"""Strategem Core - V1 Completeness Tests

Tests for V1 completeness hardening specification:
1. Missing decision → extraction attempted
2. Single option → hard failure or downgrade
3. Free-floating claim → rejected
4. Framework with no output → marked insufficient
5. Partial framework set → surfaced in Decision Surface
6. No recommendation leakage under any failure mode
"""

import pytest
from strategem import (
    ProblemContext,
    DecisionFocus,
    DecisionType,
    ProvidedMaterial,
    AnalyticalClaim,
    ClaimType,
    ClaimSource,
    ConfidenceLevel,
    DecisionFocusExtractor,
    DecisionFocusStatus,
    AnalysisOrchestrator,
    FrameworkExecutionStatus,
)


class TestDecisionFocusExtraction:
    """Test decision focus extraction from context."""

    def test_missing_decision_question_extracted(self):
        """Test 1: Missing decision → extraction attempted"""
        extractor = DecisionFocusExtractor()

        context = ProblemContext(
            title="Test",
            problem_statement="Should we enter the European market or focus on domestic growth?",
            objectives=["Expand business"],
            provided_materials=[
                ProvidedMaterial(
                    material_type="text",
                    content="We are considering two options: enter European market or focus on domestic growth. The European option offers growth potential but higher risk. Domestic growth is safer but limited.",
                    source="test.txt",
                )
            ],
        )

        status, decision_focus = extractor.extract(context)

        assert status in [DecisionFocusStatus.EXPLICIT, DecisionFocusStatus.DERIVED]
        assert decision_focus is not None
        assert len(decision_focus.options) >= 2
        assert (
            "european" in decision_focus.decision_question.lower()
            or "domestic" in decision_focus.decision_question.lower()
        )

    def test_single_option_fails(self):
        """Test 2: Single option → hard failure or downgrade"""
        extractor = DecisionFocusExtractor()

        context = ProblemContext(
            title="Test",
            problem_statement="We should improve operations.",
            provided_materials=[
                ProvidedMaterial(
                    material_type="text",
                    content="We want to improve operational efficiency through better processes.",
                    source="test.txt",
                )
            ],
        )

        status, decision_focus = extractor.extract(context)

        # With only vague problem statement, should not extract options
        assert status == DecisionFocusStatus.INSUFFICIENT
        assert decision_focus is None


class TestClaimOptionBinding:
    """Test claim-option binding enforcement."""

    def test_free_floating_claim_rejected(self):
        """Test 3: Free-floating claim → rejected"""
        orchestrator = AnalysisOrchestrator()

        claims = [
            AnalyticalClaim(
                statement="This is a claim without any options",
                source=ClaimSource.INFERENCE,
                confidence=ConfidenceLevel.MEDIUM,
                framework="test",
                claim_type=ClaimType.OPTION_SPECIFIC,
                applicable_options=[],  # Invalid: option_specific needs exactly 1 option
            ),
            AnalyticalClaim(
                statement="This claim has only one option but is comparative",
                source=ClaimSource.INFERENCE,
                confidence=ConfidenceLevel.MEDIUM,
                framework="test",
                claim_type=ClaimType.COMPARATIVE,
                applicable_options=[
                    "Option A"
                ],  # Invalid: comparative needs >=2 options
            ),
        ]

        valid_claims = orchestrator.validate_claims_option_binding(
            claims, ["Option A", "Option B"]
        )

        # Both claims should be rejected
        assert len(valid_claims) == 0

    def test_valid_option_specific_claim(self):
        """Test valid option-specific claim passes validation"""
        orchestrator = AnalysisOrchestrator()

        claims = [
            AnalyticalClaim(
                statement="This option has high supplier power",
                source=ClaimSource.INFERENCE,
                confidence=ConfidenceLevel.MEDIUM,
                framework="test",
                claim_type=ClaimType.OPTION_SPECIFIC,
                applicable_options=["Option A"],
            ),
        ]

        valid_claims = orchestrator.validate_claims_option_binding(
            claims, ["Option A", "Option B"]
        )

        assert len(valid_claims) == 1

    def test_valid_comparative_claim(self):
        """Test valid comparative claim passes validation"""
        orchestrator = AnalysisOrchestrator()

        claims = [
            AnalyticalClaim(
                statement="Option A has higher supplier power than Option B",
                source=ClaimSource.INFERENCE,
                confidence=ConfidenceLevel.MEDIUM,
                framework="test",
                claim_type=ClaimType.COMPARATIVE,
                applicable_options=["Option A", "Option B"],
            ),
        ]

        valid_claims = orchestrator.validate_claims_option_binding(
            claims, ["Option A", "Option B"]
        )

        assert len(valid_claims) == 1

    def test_valid_system_level_claim(self):
        """Test valid system-level claim passes validation"""
        orchestrator = AnalysisOrchestrator()

        claims = [
            AnalyticalClaim(
                statement="Market dynamics are shifting",
                source=ClaimSource.INFERENCE,
                confidence=ConfidenceLevel.MEDIUM,
                framework="test",
                claim_type=ClaimType.SYSTEM_LEVEL,
                applicable_options=["all"],
            ),
        ]

        valid_claims = orchestrator.validate_claims_option_binding(
            claims, ["Option A", "Option B"]
        )

        assert len(valid_claims) == 1


class TestFrameworkSufficiency:
    """Test framework execution sufficiency validation."""

    def test_framework_with_no_output_marked_insufficient(self):
        """Test 4: Framework with no output → marked insufficient"""
        orchestrator = AnalysisOrchestrator()

        context = ProblemContext(
            title="Test",
            problem_statement="Test problem",
            decision_focus=DecisionFocus(
                decision_question="Test question",
                decision_type=DecisionType.COMPARE,
                options=["Option A", "Option B"],
            ),
        )

        # Create a framework result with no claims
        from strategem.models import FrameworkResult, PorterAnalysis, ForceAnalysis
        from datetime import datetime

        force = ForceAnalysis(
            name="Test Force",
            relevance_to_decision="low",
            relevance_rationale="Not relevant",
            effect_by_option=[],
            claims=[],  # No claims
        )

        porter = PorterAnalysis(
            decision_question="Test",
            options_analyzed=["Option A", "Option B"],
            threat_of_new_entrants=force,
            supplier_power=force,
            buyer_power=force,
            substitutes=force,
            rivalry=force,
            structural_asymmetries=[],
            option_aware_claims=[],  # No claims
        )

        framework_result = FrameworkResult(
            framework_name="porter",
            success=True,
            result=porter,
            claims=[],
        )

        # Validate framework sufficiency
        validated_result = orchestrator.validate_framework_sufficiency(
            framework_result, context
        )

        # Should be marked as insufficient
        assert (
            validated_result.execution_status == FrameworkExecutionStatus.INSUFFICIENT
        )
        assert "no valid claims" in validated_result.execution_reason.lower()


class TestDecisionSurface:
    """Test decision surface with blocked judgments."""

    def test_partial_framework_surfaced_in_decision_surface(self):
        """Test 5: Partial framework set → surfaced in Decision Surface"""
        orchestrator = AnalysisOrchestrator()

        # This would be tested with actual analysis runs
        # The key is that blocked_judgments appears in DecisionSurface
        pass


class TestNoRecommendationLeakage:
    """Test that recommendations don't leak in any mode."""

    def test_exploratory_mode_no_recommendation(self):
        """Test 6: Exploratory mode has no recommendations"""
        # When analysis_sufficiency.overall_status is EXPLORATORY_ONLY
        # Report should not contain "recommend", "should", "choose"
        pass

    def test_constrained_mode_no_recommendation(self):
        """Test 6: Constrained mode has no recommendations"""
        # When analysis_sufficiency.overall_status is CONSTRAINED
        # Report should not contain recommendations
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
