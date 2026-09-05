class ConversationManager:
    """
    Manages conversational state for ClarifySQL.

    Stores pending clarification questions and resolved
    conversation context for each session.
    """

    def __init__(self):

        self.pending_clarifications = {}

        self.conversation_context = {}

    # ============================================================
    # CLARIFICATION MANAGEMENT
    # ============================================================

    def store_clarification(
        self,
        session_id,
        original_question,
        clarification_id,
        clarification,
        options
    ):

        self.pending_clarifications[session_id] = {
            "original_question": original_question,
            "clarification_id": clarification_id,
            "clarification": clarification,
            "options": options
        }

    def has_pending_clarification(
        self,
        session_id
    ):

        return (
            session_id
            in self.pending_clarifications
        )

    def get_pending_clarification(
        self,
        session_id
    ):

        return self.pending_clarifications.get(
            session_id
        )

    # ============================================================
    # ANSWER MATCHING
    # ============================================================

    def _match_answer(
        self,
        answer,
        options
    ):

        if not answer:

            return None

        answer_lower = answer.lower().strip()

        # --------------------------------------------------------
        # OPTION NUMBER
        # --------------------------------------------------------

        if answer_lower.isdigit():

            option_number = int(
                answer_lower
            )

            if (
                option_number >= 1
                and option_number <= len(options)
            ):

                return options[
                    option_number - 1
                ]

        # --------------------------------------------------------
        # EXACT MATCH
        # --------------------------------------------------------

        for option in options:

            option_id = (
                option["id"]
                .lower()
                .strip()
            )

            option_label = (
                option["label"]
                .lower()
                .strip()
            )

            if answer_lower == option_id:

                return option

            if answer_lower == option_label:

                return option

        # --------------------------------------------------------
        # WORD MATCH
        # --------------------------------------------------------

        answer_words = set(
            answer_lower.split()
        )

        for option in options:

            option_text = (
                option["id"].lower()
                + " "
                + option["label"].lower()
            )

            option_words = set(
                option_text.split()
            )

            if answer_words.intersection(
                option_words
            ):

                return option

        return None

    # ============================================================
    # RESOLVE CLARIFICATION
    # ============================================================

    def resolve_clarification(
        self,
        session_id,
        answer
    ):

        if not self.has_pending_clarification(
            session_id
        ):

            return {
                "resolved": False,
                "message": (
                    "There is no pending "
                    "clarification."
                ),
                "options": []
            }

        conversation = (
            self.pending_clarifications[
                session_id
            ]
        )

        original_question = (
            conversation[
                "original_question"
            ]
        )

        clarification = (
            conversation[
                "clarification"
            ]
        )

        options = (
            conversation[
                "options"
            ]
        )

        clarification_id = (
            conversation[
                "clarification_id"
            ]
        )

        selected_option = (
            self._match_answer(
                answer,
                options
            )
        )

        # --------------------------------------------------------
        # INVALID ANSWER
        # --------------------------------------------------------

        if selected_option is None:

            return {
                "resolved": False,
                "message": clarification,
                "options": options
            }

        # --------------------------------------------------------
        # BUILD COMPLETED QUESTION
        # --------------------------------------------------------

        completed_question = (
            f"{original_question} "
            f"Measure it using "
            f"{selected_option['label']}."
        )

        # --------------------------------------------------------
        # STORE RESOLVED CONTEXT
        # --------------------------------------------------------

        self.conversation_context[
            session_id
        ] = {
            "original_question": original_question,
            "clarification_id": clarification_id,
            "selected_option": selected_option,
            "completed_question": completed_question
        }

        # --------------------------------------------------------
        # REMOVE PENDING CLARIFICATION
        # --------------------------------------------------------

        del self.pending_clarifications[
            session_id
        ]

        return {
            "resolved": True,
            "question": completed_question,
            "selected_option": selected_option
        }

    # ============================================================
    # CONTEXT
    # ============================================================

    def get_context(
        self,
        session_id
    ):

        return self.conversation_context.get(
            session_id
        )

    def clear_context(
        self,
        session_id
    ):

        self.pending_clarifications.pop(
            session_id,
            None
        )

        self.conversation_context.pop(
            session_id,
            None
        )


conversation_manager = ConversationManager()