from typing import Optional
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    limit: int = 20
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    
    def validate(self) -> None:
        """Validate pagination parameters."""
        if self.page < 1:
            raise ValueError("Page must be greater than 0")
        
        if self.limit < 1 or self.limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        if self.sort_order not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
    
    @property
    def offset(self) -> int:
        """Calculate offset for SQL query."""
        return (self.page - 1) * self.limit