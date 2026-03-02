from pydantic import BaseModel, Field


class CreateProjectPayload(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description= "Project Length Must be Less Than 100")
    open_after_create: bool


class OpenProjectPayload(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)


class RenameProjectPayload(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)
    new_name: str = Field(..., min_length=1, max_length=100)


class DeleteProjectPayload(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=100)
    confirm_name: str = Field(..., min_length=1, max_length=100)


class ChangeProjectPayload(BaseModel):
    modal: str
    new_project_name: str = Field(..., min_length=1, max_length=100)
