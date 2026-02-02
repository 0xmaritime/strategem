"""Strategem Core - Decision Focus Extractor (V1 Completeness Hardening)

This module extracts implied decision focus from problem context when explicit
decision_focus is not provided by the user.
"""

import re
from typing import Optional, List, Tuple
from .models import (
    ProblemContext,
    DecisionFocus,
    DecisionFocusStatus,
    DecisionType,
)


class DecisionFocusExtractor:
    """
    Extracts implied decision focus from problem context materials.

    If decision_focus is not explicitly provided, this module attempts to derive:
    - Implied decision question
    - Candidate options from headings, enumerations, contrasts
    - Decision type

    Returns confidence score for extraction.
    """

    def __init__(self):
        # Patterns that suggest decision questions
        self.question_patterns = [
            r"should\s+(?:we|i)\s+(.+?)[??.\n]",
            r"(?:decide|choose|select|pick)\s+between\s+(.+)",
            r"considering\s+(.+?)\s+vs\.?\s+(.+)",
            r"(?:compare|evaluate|assess)\s+(.+)",
            r"what\s+(?:to|should)\s+(?:we|i)\s+do\s+(?:about|with)?\s*(.+?)[??.\n]",
        ]

        # Patterns that suggest options
        self.option_patterns = [
            r"option\s+(\d+)[:\s]+(.+?)(?:\n|$)",
            r"(?:choice|alternative|path)\s+(\d+)[:\s]+(.+?)(?:\n|$)",
            r"(?:vs\.?|versus|or|,)\s*([A-Z][^.?!\n]+)",
            r"(?:approach\s+)(\w+)[:\s]+(.+?)(?:\n|$)",
        ]

    def extract(
        self, context: ProblemContext
    ) -> Tuple[DecisionFocusStatus, Optional[DecisionFocus]]:
        """
        Extract decision focus from problem context.

        Args:
            context: The problem context to analyze

        Returns:
            Tuple of (status, decision_focus)
            - status: EXPLICIT, DERIVED, or INSUFFICIENT
            - decision_focus: DecisionFocus object if EXPLICIT or DERIVED, None if INSUFFICIENT
        """
        # Check if decision_focus is already explicit
        if context.decision_focus:
            self._validate_explicit_decision_focus(context.decision_focus)
            return DecisionFocusStatus.EXPLICIT, context.decision_focus

        # Attempt to derive decision focus from context
        decision_focus = self._derive_decision_focus(context)

        if decision_focus:
            return DecisionFocusStatus.DERIVED, decision_focus
        else:
            return DecisionFocusStatus.INSUFFICIENT, None

    def _validate_explicit_decision_focus(self, decision_focus: DecisionFocus):
        """
        Validate that explicit decision focus meets minimum requirements.

        V1 Requirement: At least 2 options required for meaningful analysis.
        """
        if len(decision_focus.options) < 2:
            raise ValueError(
                f"Decision focus requires at least 2 options. "
                f"Only {len(decision_focus.options)} provided: {decision_focus.options}"
            )

        if not decision_focus.decision_question.strip():
            raise ValueError("Decision question cannot be empty")

    def _derive_decision_focus(
        self, context: ProblemContext
    ) -> Optional[DecisionFocus]:
        """
        Derive decision focus from problem context materials.

        Returns:
            DecisionFocus with low confidence if extraction successful, None otherwise
        """
        # Collect all text content from materials
        full_text = self._collect_text_content(context)

        if not full_text or len(full_text) < 100:
            return None

        # Extract decision question
        decision_question = self._extract_decision_question(full_text, context)
        if not decision_question:
            return None

        # Extract options
        options = self._extract_options(full_text, context)
        if len(options) < 2:
            return None

        # Infer decision type
        decision_type = self._infer_decision_type(decision_question, options)

        return DecisionFocus(
            decision_question=decision_question,
            decision_type=decision_type,
            options=options,
        )

    def _collect_text_content(self, context: ProblemContext) -> str:
        """Collect all text content from problem context materials."""
        text_parts = []

        # From provided materials
        for material in context.provided_materials:
            text_parts.append(material.content)

        # From problem statement
        if context.problem_statement:
            text_parts.append(context.problem_statement)

        # From objectives
        if context.objectives:
            text_parts.extend(context.objectives)

        return " ".join(text_parts)

    def _extract_decision_question(
        self, text: str, context: ProblemContext
    ) -> Optional[str]:
        """Extract implied decision question from text."""
        # Try regex patterns first
        for pattern in self.question_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                question_text = match.group(1).strip()
                # Clean up the question text
                question_text = re.sub(r"\s+", " ", question_text)
                question_text = question_text.strip(" .,?!")

                # Ensure it's a proper question
                if not question_text.endswith("?"):
                    question_text += "?"

                return question_text

        # Try to infer from problem statement
        if context.problem_statement:
            problem_stmt = context.problem_statement.strip().lower()
            if any(
                word in problem_stmt
                for word in ["should", "decide", "choose", "select"]
            ):
                # Use problem statement as decision question
                question = context.problem_statement.strip()
                if not question.endswith("?"):
                    question += "?"
                return question

        return None

    def _extract_options(self, text: str, context: ProblemContext) -> List[str]:
        """Extract candidate options from text."""
        options = set()

        # Try regex patterns
        for pattern in self.option_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Try to capture from both numbered options and "vs" contrasts
                if match.lastindex == 2:
                    option_text = match.group(2).strip()
                else:
                    option_text = match.group(1).strip()

                if option_text and len(option_text) > 3:
                    options.add(option_text)

        # Extract from objectives that sound like options
        if context.objectives:
            for obj in context.objectives:
                obj_lower = obj.lower()
                # Skip objectives that are general goals
                if any(
                    skip in obj_lower
                    for skip in ["increase", "reduce", "improve", "achieve"]
                ):
                    continue
                # Objectives that sound like alternative approaches
                if any(
                    keyword in obj_lower
                    for keyword in ["alternative", "approach", "option", "strategy"]
                ):
                    options.add(obj.strip())

        # Extract from numbered headings or lists
        numbered_options = re.findall(r"^\s*\d+\.\s*([^.?!\n]+)", text, re.MULTILINE)
        for opt in numbered_options:
            opt_clean = opt.strip()
            if len(opt_clean) > 5:  # Filter out short fragments
                options.add(opt_clean)

        # Extract from bullet points in specific contexts
        bullet_options = re.findall(r"[-*]\s*([^.?!\n]{10,})", text)
        for opt in bullet_options[:10]:  # Limit to top 10 to avoid noise
            options.add(opt.strip())

        # Return top 5 options, cleaned
        sorted_options = sorted(options, key=len, reverse=True)
        return sorted_options[:5]

    def _infer_decision_type(
        self, decision_question: str, options: List[str]
    ) -> DecisionType:
        """
        Infer decision type from question and options.

        Rules:
        - COMPARE: If question contains "vs", "versus", "compare", or 2-3 specific options
        - EXPLORE: If question is open-ended or has 4+ options
        - STRESS_TEST: If question contains "stress test", "scenario", "what if"
        """
        question_lower = decision_question.lower()

        # Check for stress test keywords
        if any(
            keyword in question_lower
            for keyword in ["stress test", "scenario", "what if", "if we", "assuming"]
        ):
            return DecisionType.STRESS_TEST

        # Check for comparison keywords
        if any(
            keyword in question_lower
            for keyword in ["vs", "versus", "compare", "between", "choose between"]
        ):
            return DecisionType.COMPARE

        # Decision based on number of options
        if len(options) <= 3:
            return DecisionType.COMPARE
        elif len(options) >= 5:
            return DecisionType.EXPLORE
        else:
            return DecisionType.EXPLORE
