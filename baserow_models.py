from dataclasses import dataclass
from typing import List
from pydantic import AliasPath, BaseModel, Field

class SurveyStatus:
    CLOSED = 3
    ARCHIVE = 4
    OPEN = 5

class BaseRecord(BaseModel):
    id: int
    name: str = Field(alias="value")


class SurveyRecord(BaseModel):
    id: int
    contact: BaseRecord = Field(validation_alias=AliasPath("איש קשר", 0))
    inspector: BaseRecord = Field(validation_alias=AliasPath("בוחן", 0))
    type: BaseRecord = Field(alias="סוג בדיקה")
    machine: BaseRecord = Field(validation_alias=AliasPath("מכונת הרמה", 0))
    defiencies: List[BaseRecord] = Field(alias="ליקויים")


class Machine(BaseModel):
    id: int
    description: str  # = Field(alias="תיאור מכונת הרמה")
    full_description: str = Field(alias="תיאור מפורט")
    model: str = Field(alias="דגם")
    producer: str = Field(alias="יצרן")


class Contact(BaseModel):
    id: int
    name: str = Field(alias="שם")
    phone: str = Field(alias="טלפון")
    stationary_phone: str = Field(alias="טלפון נייח")
    fax: str = Field(alias="פקס")
    email: str = Field(alias="מייל")


@dataclass
class Survey:
    id: int
    contact: Contact
    machine: Machine
