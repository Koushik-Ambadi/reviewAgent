# src/repo_review/pipeline/stage.py

from __future__ import annotations

from abc import ABC, abstractmethod

from .context import PipelineContext


class PipelineStage(ABC):
    """
    Base class for all pipeline stages.

    Every stage:
        - receives PipelineContext
        - updates only its own results
        - returns structured stage output
    """

    stage_name = "base_stage"

    def __init__(self, context: PipelineContext):
        self.context = context

    # =========================================================
    # MAIN EXECUTION
    # =========================================================

    def execute(self) -> dict:
        """
        Unified execution wrapper.

        Handles:
            - stage execution
            - structured success response
            - structured failure response
        """

        try:
            result = self.run()

            if not isinstance(result, dict):
                raise TypeError(
                    f"{self.stage_name} must return dict"
                )

            result.setdefault("status", "success")

            return result

        except Exception as e:
            return {
                "status": "failed",
                "stage": self.stage_name,
                "error": str(e),
            }

    # =========================================================
    # STAGE IMPLEMENTATION
    # =========================================================

    @abstractmethod
    def run(self) -> dict:
        """
        Actual stage implementation.
        """
        raise NotImplementedError