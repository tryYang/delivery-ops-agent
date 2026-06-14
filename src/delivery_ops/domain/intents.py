from __future__ import annotations

from enum import Enum


class TaskIntent(str, Enum):
    LIST_SERIOUS_BUGS = "list_serious_bugs"
    ANALYZE_BUG = "analyze_bug"
    GENERATE_FIX_ORDER = "generate_fix_order"
    LIST_FEATURE_TASKS = "list_feature_tasks"
    ANALYZE_FEATURE = "analyze_feature"
    GENERATE_FEATURE_ORDER = "generate_feature_order"
    TASK_STATUS = "task_status"
    CANCEL_TASK = "cancel_task"
    UNKNOWN = "unknown"


class WorkflowType(str, Enum):
    BUG_FIX = "bug_fix"
    FEATURE_DEVELOPMENT = "feature_development"
    SYSTEM = "system"
