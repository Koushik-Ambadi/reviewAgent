@dataclass
class ReviewIssue:
    category: str
    rule: str
    severity: str
    status: str

    file: str
    line: int | None

    symbol: str | None

    message: str