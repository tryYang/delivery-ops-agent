from __future__ import annotations

from datetime import UTC, datetime

from delivery_ops.application.report_publisher import ReportPublisher
from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.tasks import TaskSnapshot, TaskStatus


class TestReportPublisher:
    def setup_method(self) -> None:
        self.publisher = ReportPublisher()
        self.snapshot = TaskSnapshot(
            task_id="task-1",
            workflow_type=WorkflowType.BUG_FIX,
            intent=TaskIntent.LIST_SERIOUS_BUGS,
            status=TaskStatus.ANALYZING,
            user_id="user-1",
            input_text="serious bug",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    def test_bug_placeholder_message(self) -> None:
        report = self.publisher.build(self.snapshot, TaskIntent.LIST_SERIOUS_BUGS)
        assert report.message == "Bug Fix workflow placeholder ready"

    def test_feature_placeholder_message(self) -> None:
        feature_snapshot = self.snapshot.model_copy(
            update={
                "workflow_type": WorkflowType.FEATURE_DEVELOPMENT,
                "intent": TaskIntent.LIST_FEATURE_TASKS,
            }
        )
        report = self.publisher.build(feature_snapshot, TaskIntent.LIST_FEATURE_TASKS)
        assert report.message == "Feature workflow placeholder ready"

    def test_unknown_message(self) -> None:
        report = self.publisher.build_unknown()
        assert report.message == "Intent not recognized."
        assert report.task_id == ""
