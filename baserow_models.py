from dataclasses import dataclass
from typing import List
from pydantic import AliasPath, BaseModel, Field


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
