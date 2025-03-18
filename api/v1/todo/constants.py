class TodoStatus:
    PENDING = "pending"
    COMPLETED = "completed"

class TodoPriority:
    MIN = 1
    MAX = 5
    LOW = 1
    MEDIUM = 3
    HIGH = 5

class DashboardMemberRole:
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

    @classmethod
    def choices(cls) -> list:
        return [
            (cls.OWNER, "Owner"),
            (cls.EDITOR, "Editor"),
            (cls.VIEWER, "Viewer"),
        ] 