from datetime import datetime

from pydantic import BaseModel, Field


class OpportunitySelectionCreate(BaseModel):
    selection_reason: str | None = Field(
        default=None,
        max_length=2000,
        description="Why the founder selected this opportunity"
    )


class OpportunitySelectionResponse(BaseModel):
    id: int
    founder_id: int
    opportunity_id: int
    selection_reason: str | None
    selected_at: datetime

    model_config = {
        "from_attributes": True
    }


class OpportunitySelectionResult(BaseModel):
    message: str
    selection: OpportunitySelectionResponse
    startup_id: int
    startup_name: str
    journey_type: str