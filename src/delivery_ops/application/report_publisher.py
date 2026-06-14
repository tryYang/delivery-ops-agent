from __future__ import annotations

from delivery_ops.domain.bugfix import BugFixArtifacts
from delivery_ops.domain.features import FeatureArtifacts
from delivery_ops.domain.intents import TaskIntent, WorkflowType
from delivery_ops.domain.reports import AgentReport
from delivery_ops.domain.tasks import TaskSnapshot, TaskStatus


class ReportPublisher:
    """将 TaskSnapshot 转为用户可读 AgentReport。"""

    _PLACEHOLDER_MESSAGES: dict[TaskIntent, str] = {
        TaskIntent.LIST_SERIOUS_BUGS: "Top serious bugs ranked.",
        TaskIntent.ANALYZE_BUG: "Bug evidence packet ready.",
        TaskIntent.GENERATE_FIX_ORDER: "Fix work order compiled.",
        TaskIntent.LIST_FEATURE_TASKS: "Top feature candidates ranked.",
        TaskIntent.ANALYZE_FEATURE: "Feature evidence packet ready.",
        TaskIntent.GENERATE_FEATURE_ORDER: "Feature work order compiled.",
        TaskIntent.TASK_STATUS: "Task status retrieved (placeholder).",
        TaskIntent.CANCEL_TASK: "Task cancellation processed (placeholder).",
        TaskIntent.UNKNOWN: "Intent not recognized.",
    }

    def build(
        self,
        snapshot: TaskSnapshot,
        intent: TaskIntent,
        bugfix: BugFixArtifacts | None = None,
        feature: FeatureArtifacts | None = None,
        error: str | None = None,
    ) -> AgentReport:
        if error:
            message = error
        elif bugfix is not None and intent == TaskIntent.LIST_SERIOUS_BUGS and bugfix.top_bugs:
            message = f"Returned {len(bugfix.top_bugs)} serious bug candidates."
        elif bugfix is not None and intent == TaskIntent.ANALYZE_BUG and bugfix.evidence:
            message = f"Evidence built for {bugfix.evidence.bug_id}."
        elif bugfix is not None and intent == TaskIntent.GENERATE_FIX_ORDER and bugfix.work_order:
            message = f"Work order compiled for {bugfix.evidence.bug_id if bugfix.evidence else 'bug'}."
        elif feature is not None and intent == TaskIntent.LIST_FEATURE_TASKS and feature.top_features:
            message = f"Returned {len(feature.top_features)} feature candidates."
        elif feature is not None and intent == TaskIntent.ANALYZE_FEATURE and feature.evidence:
            message = f"Evidence built for {feature.evidence.feature_id}."
        elif feature is not None and intent == TaskIntent.GENERATE_FEATURE_ORDER and feature.work_order:
            fid = feature.evidence.feature_id if feature.evidence else "feature"
            message = f"Work order compiled for {fid}."
        else:
            message = self._PLACEHOLDER_MESSAGES.get(intent, "Request processed (placeholder).")

        return AgentReport(
            task_id=snapshot.task_id,
            workflow_type=snapshot.workflow_type,
            intent=intent,
            status=snapshot.status,
            message=message,
            details={
                "input_text": snapshot.input_text,
                "user_id": snapshot.user_id,
            },
            bugfix=bugfix,
            feature=feature,
        )

    def build_unknown(self, intent: TaskIntent = TaskIntent.UNKNOWN) -> AgentReport:
        return AgentReport(
            task_id="",
            workflow_type=WorkflowType.SYSTEM,
            intent=intent,
            status=TaskStatus.CREATED,
            message=self._PLACEHOLDER_MESSAGES[TaskIntent.UNKNOWN],
            details={},
        )
