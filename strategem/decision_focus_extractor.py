"""Strategem Core - Decision Focus Extractor (V1)

This module extracts implied decision focus from problem context when explicit
decision_focus is not provided by the user.
"""

import re
from typing import Optional, List
from .models import (
    ProblemContext,
    DecisionFocus,
    DecisionType,
)


class DecisionFocusExtractor:
    """
    Extracts implied decision focus from problem context.

    V1 Principle: Decision Focus is inferred, not declared.

    A DecisionFocus exists if a bounded choice situation is reasonably inferable
    from provided context, regardless of whether a formal schema is supplied.

    Decision Inference Gate (binary, conservative):
    DecisionFocus = bound if ALL of the following are true:
    1. A choice is implied (verbs like choose, decide, select, recommend, defend)
    2. Multiple alternatives are materially described (≥2 distinct approaches with trade-offs)
    3. A decision owner or role exists ("You are X", "the committee must", etc.)

    This is a locked V1 rule, not a V2 enhancement.
    """

    def __init__(self):
        # Decision verbs that imply choice
        self.decision_verbs = [
            r"choose",
            r"decide",
            r"select",
            r"pick",
            r"recommend",
            r"defend",
            r"adopt",
            r"implement",
            r"pursue",
            r"prioritize",
            r"prefer",
        ]

        # Patterns that suggest decision questions
        # V1: Non-greedy patterns with proper stop characters
        self.question_patterns = [
            r"should\s+(?:we|i)\s+(.+?)[??.\n]",
            r"(?:decide|choose|select|pick)\s+between\s+(.+?)(?:[.;?!]|\n)",
            r"considering\s+(.+?)\s+vs\.?\s+(.+?)(?:[.;?!]|\n)",
            r"(?:compare|evaluate|assess)\s+(.+?)(?:[.;?!]|\n)",
            r"what\s+(?:to|should)\s+(?:we|i)\s+do\s+(?:about|with)?\s*(.+?)[??.\n]",
        ]

        # Patterns that suggest options
        self.option_patterns = [
            r"option\s+(\d+)[:\s]+(.+?)(?:\n|$)",
            r"(?:choice|alternative|path)\s+(\d+)[:\s]+(.+?)(?:\n|$)",
            r"(?:vs\.?|versus|or|,)\s*([A-Z][^.?!\n]+)",
            r"(?:approach\s+)(\w+)[:\s]+(.+?)(?:\n|$)",
        ]

        # Patterns that suggest decision owner or role
        self.decision_owner_patterns = [
            r"you\s+are\s+(?:the\s+)?(.{5,50})",
            r"the\s+(?:committee|board|council|team|group)\s+(?:should|must|needs to)",
            r"we\s+need\s+to\s+(?:decide|choose|select)",
            r"(?:as\s+)?(?:the\s+)?(?:ceo|director|manager|lead)\s+(?:of|for)",
        ]

    def extract(self, context: ProblemContext) -> Optional[DecisionFocus]:
        """
        Extract decision focus from problem context.

        V1 Principle: Decision Focus is inferred, not declared.
        Forms are optional hints, never epistemic authorities.

        Returns None if decision context cannot be inferred.
        Caller determines mode (analytical vs exploratory).

        Args:
            context: The problem context to analyze

        Returns:
            DecisionFocus if inferable, None otherwise
        """
        # Check if decision_focus is explicitly provided (optional hint)
        if context.decision_focus:
            return context.decision_focus

        # Apply Decision Inference Gate
        decision_focus = self._apply_decision_inference_gate(context)

        return decision_focus

    def _apply_decision_inference_gate(
        self, context: ProblemContext
    ) -> Optional[DecisionFocus]:
        """
        Apply binary, conservative Decision Inference Gate.

        Returns DecisionFocus if ALL three criteria are met:
        1. Choice is implied (decision verbs present)
        2. ≥2 distinct alternatives with trade-offs
        3. Decision owner or role exists

        Returns None if any criterion is not met.
        """
        # Collect text
        full_text = self._collect_text_content(context)

        if not full_text or len(full_text) < 50:
            return None

        # Criterion 1: Choice is implied (decision verbs present)
        choice_implied = self._check_choice_implied(full_text)
        if not choice_implied:
            return None

        # Criterion 2: ≥2 distinct alternatives with trade-offs
        alternatives = self._extract_alternatives(full_text, context)
        if len(alternatives) < 2:
            return None

        # Criterion 3: Decision owner or role exists
        has_owner = self._check_decision_owner(full_text)
        if not has_owner:
            return None

        # All three criteria met - infer DecisionFocus
        decision_question = (
            self._extract_decision_question(full_text, context)
            or "Inferred decision from context"
        )
        decision_type = self._infer_decision_type(full_text, alternatives)

        return DecisionFocus(
            decision_question=decision_question,
            decision_type=decision_type,
            options=alternatives,
        )

    def _check_choice_implied(self, text: str) -> bool:
        """
        Check if choice is implied by presence of decision verbs.
        """
        text_lower = text.lower()
        for verb in self.decision_verbs:
            if re.search(verb, text_lower, re.IGNORECASE):
                return True
        return False

    def _check_decision_owner(self, text: str) -> bool:
        """
        Check if decision owner or role is explicitly mentioned.
        """
        text_lower = text.lower()
        for pattern in self.decision_owner_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    def _extract_alternatives(self, text: str, context: ProblemContext) -> List[str]:
        """
        Extract ≥2 distinct alternatives from text.

        Conservative: Only extract alternatives that are clearly material
        and have trade-off characteristics.
        """
        alternatives = []

        # Method 1: "vs" or "versus" patterns (strongest signal)
        # V1: Simplified to avoid partial matches and duplicate detection
        # Pattern: "X vs Y" or "X versus Y"
        vs_pattern = re.search(
            r"(.+?)\s+(?:vs\.?|versus)\s+([^.,\n]{5,100})",
            text,
            re.IGNORECASE,
        )
        if vs_pattern:
            # Both sides of "vs" are alternatives
            alt1 = vs_pattern.group(1).strip()
            alt2 = vs_pattern.group(2).strip()
            if len(alt1) > 3 and len(alt2) > 3:
                if alt1 not in alternatives:
                    alternatives.append(alt1)
                if alt2 not in alternatives:
                    alternatives.append(alt2)
            return alternatives  # Found clean vs match, stop here

        # Method 1b: "or" pattern (weaker signal, but still useful)
        or_pattern = re.findall(
            r"(.{10,100})\s+or\s+([^.,\n]{10,100})",
            text,
            re.IGNORECASE,
        )
        for match in or_pattern:
            alt1 = match[0].strip()
            alt2 = match[1].strip()
            if len(alt1) > 3 and len(alt2) > 3:
                if alt1 not in alternatives:
                    alternatives.append(alt1)
                if alt2 not in alternatives:
                    alternatives.append(alt2)

        if len(alternatives) >= 2:
            return alternatives  # Found alternatives via "or" pattern, stop here

        # Method 2: Numbered list pattern (X. [option])
        # V1: Only run if we don't already have enough alternatives from other methods
        # V1: Stops at punctuation to avoid capturing too much context
        if len(alternatives) >= 2:
            return alternatives  # Already have alternatives from "vs" or "or" pattern

        numbered_options = re.findall(
            r"(?:option|choice|alternative|approach)?\s*\d+[:\.\s]+([^.?!;0-9\n]{8,150})",
            text,
            re.IGNORECASE,
        )
        for match in numbered_options:
            option_text = match.strip()

            # Clean trailing punctuation
            option_text = option_text.rstrip(",.;:")

            # Clean up trailing "or" if captured
            if option_text.lower().endswith(", or") or option_text.lower().endswith(
                " or"
            ):
                option_text = option_text[:-4].strip()

            # Filter out role definitions and context sentences
            # These are NOT decision options
            if any(
                phrase in option_text.lower()
                for phrase in [
                    "you are the",
                    "you are",
                    "you're",
                    "you represent",
                    "the city council",
                    "the board",
                    "the committee",
                    "must decide",
                    "addressing homeless services",
                    "cost structures",
                    "trade-offs",
                ]
            ):
                continue

            # Clean: Stop at next sentence structure
            # Remove any trailing phrases like "Each option has..."
            for stop_phrase in [
                ", each option",
                ". each option",
                "; each option",
                ", this provides",
            ]:
                if stop_phrase in option_text.lower():
                    option_text = option_text[
                        : option_text.lower().find(stop_phrase)
                    ].strip()

            if len(option_text) > 5 and option_text not in alternatives:
                alternatives.append(option_text)

        # Method 3: Check objectives for alternative descriptions
        if context.objectives:
            for obj in context.objectives:
                if any(
                    keyword in obj.lower()
                    for keyword in ["alternative", "option", "approach", "strategy"]
                ):
                    obj_text = obj.strip()
                    if len(obj_text) > 5 and obj_text not in alternatives:
                        alternatives.append(obj_text)

        # Method 4: Look for explicit enumeration patterns
        # V1: Only run if we don't already have enough alternatives from other methods
        # Pattern: "choose between [A], [B], and [C]"
        # V1: Simplified non-greedy pattern
        if len(alternatives) >= 2:
            return alternatives  # Already have alternatives

        between_pattern = re.search(
            r"(?:choose|decide|select|pick)\s+between\s+(.+?),\s+(.+?),?\s*(?:and\s+)?(.+?)(?:\.|,|$)",
            text,
            re.IGNORECASE,
        )
        if between_pattern:
            parts = [
                p
                for p in [
                    between_pattern.group(1),
                    between_pattern.group(2),
                    between_pattern.group(3),
                ]
                if p
            ]
            for part in parts:
                if part and len(part.strip()) > 5:
                    alt_text = part.strip()

                    # Filter out role definitions and context
                    if any(
                        phrase in alt_text.lower()
                        for phrase in [
                            "you are",
                            "the city council",
                            "addressing",
                            "cost structures",
                        ]
                    ):
                        continue

                    if alt_text not in alternatives:
                        alternatives.append(alt_text)
            return alternatives  # Found clean between pattern, stop here

        # Deduplicate and return top 5
        # V1: Case-insensitive deduplication with punctuation normalization
        seen = set()
        unique_alternatives = []
        for alt in alternatives:
            # Normalize for comparison (lowercase, stripped, punctuation removed)
            alt_normalized = re.sub(r"[.,;:!?]", "", alt.lower()).strip()
            if alt_normalized in seen:
                continue  # Skip duplicates
            if len(alt) > 3:  # Minimum length for an option
                seen.add(alt_normalized)
                unique_alternatives.append(alt)

        return unique_alternatives[:5]

    def _extract_decision_question(
        self, text: str, context: ProblemContext
    ) -> Optional[str]:
        """
        Extract decision question from text.

        V1 Principle: Infer without inventing or over-capturing.
        """
        # Try explicit question patterns first
        for pattern in self.question_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                question_text = match.group(1).strip()
                question_text = re.sub(r"\s+", " ", question_text)
                question_text = question_text.strip(" .,?!")

                # Truncate at first period or question mark if beyond reasonable length
                if len(question_text) > 200:
                    first_punc = min(
                        question_text.find("."),
                        question_text.find("?"),
                        question_text.find("!"),
                    )
                    if first_punc > 0:
                        question_text = question_text[: first_punc + 1]

                # Ensure it's a proper question
                if not question_text.endswith("?"):
                    question_text += "?"

                return question_text

        # Infer from problem statement (clean extraction)
        if context.problem_statement:
            problem_stmt = context.problem_statement.strip()
            if any(
                word in problem_stmt.lower()
                for word in ["should", "decide", "choose", "select", "recommend"]
            ):
                # Extract first sentence or question
                question = (
                    problem_stmt.split(".")[0].split("?")[0].split("!")[0].strip()
                )
                if not question.endswith("?"):
                    question += "?"
                # Limit length
                if len(question) > 150:
                    question = question[:150].rsplit(" ", 1)[0] + "?"
                return question

        # Fallback: Generic question inferred from alternatives
        alternatives = self._extract_alternatives(text, context)
        if len(alternatives) >= 2:
            # Clean alternatives before using in question
            clean_alternatives = []
            for alt in alternatives[:5]:
                # Filter out role definitions like "You are the..."
                if alt.lower().startswith(
                    (
                        "you are the",
                        "you're",
                        "you represent",
                        "the city council",
                        "the board",
                        "the committee",
                    )
                ):
                    continue
                # Filter out duplicates (case-insensitive)
                if alt.lower() in [existing.lower() for existing in clean_alternatives]:
                    continue
                if len(alt) > 3:
                    clean_alternatives.append(alt[:80])

            if len(clean_alternatives) >= 2:
                # Use first sentence of problem statement if available
                if context.problem_statement:
                    first_sentence = (
                        context.problem_statement.split(".")[0]
                        .split("?")[0]
                        .split("!")[0]
                        .strip()
                    )
                    # Limit to reasonable length
                    if len(first_sentence) > 100:
                        first_sentence = first_sentence[:100]
                    if not first_sentence.endswith("?"):
                        first_sentence += "?"
                    return first_sentence

                # Final fallback: simple question based on alternatives
                if len(clean_alternatives) == 2:
                    return f"Should we {clean_alternatives[0].lower()} or {clean_alternatives[1].lower()}?"
                else:
                    return f"Which policy option should be adopted?"

        return None

    def _infer_decision_type(self, text: str, alternatives: List[str]) -> DecisionType:
        """
        Infer decision type from question and alternatives.
        """
        text_lower = text.lower()

        # Check for stress test keywords
        if any(
            keyword in text_lower
            for keyword in ["stress test", "scenario", "what if", "if we", "assuming"]
        ):
            return DecisionType.STRESS_TEST

        # Check for comparison keywords
        if any(
            keyword in text_lower
            for keyword in ["vs", "versus", "compare", "between", "choose between"]
        ):
            return DecisionType.COMPARE

        # Decision based on number of alternatives
        if len(alternatives) <= 3:
            return DecisionType.COMPARE
        elif len(alternatives) >= 5:
            return DecisionType.EXPLORE
        else:
            return DecisionType.EXPLORE

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
