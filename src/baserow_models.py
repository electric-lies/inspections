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
    creation_date: str = Field(alias="תאריך יצירה")
    next_date: str = Field(alias="תאריך בדיקה הבאה")
    previous_test_date: str = Field(alias="תאריך בדיקה קודמת")
    previous_test_id: str = Field(alias="מספר בדיקה קודמת")
    previous_test_inspector: str = Field(alias="מבצע בדיקה קודמת")
    contact: BaseRecord = Field(validation_alias=AliasPath("איש קשר", 0))
    inspector: BaseRecord = Field(validation_alias=AliasPath("בוחן", 0))
    type: BaseRecord = Field(alias="סוג בדיקה")
    machines: List[BaseRecord] = Field(alias="מכונת הרמה")
    defiencies: List[BaseRecord] = Field(alias="ליקויים")
    comments: List[BaseRecord] = Field(alias="הערות נוספות")


class LoadTest(BaseModel):
    radius: float | None = Field(alias="רדיוס")
    tested_load: float | None = Field(alias="עומס מבחן")
    safe_load: float | None = Field(alias="עומס עבודה בטוח")


#    @validator('*', pre=True)
#    def to_float(cls, v: str | None) -> float | None:
#        if v is None:
#            return None
#        return float(v)


class MachineInstance(BaseModel):
    serial_number: int = Field(alias="מספר סידורי")
    frame_number: int = Field(alias="מספר שלדה")
    certificate: str = Field(alias="מספר רישוי")
    year: int = Field(alias="שנתון")
    location: str = Field(alias="מיקום")
    inner_number: int = Field(alias="מספר פנימי")
    load_tests_records: list[BaseRecord] = Field(alias="מבחני עומס")
    X_description: list[BaseRecord] = Field(alias="תיאור")
    X_full_description: list[BaseRecord] = Field(alias="תיאור מפורט")
    X_model: list[BaseRecord] = Field(alias="דגם")
    X_producer: list[BaseRecord] = Field(alias="יצרן")
    load_tests: list[LoadTest] = Field(default=None)

    @property
    def full_description(self) -> str:
        return self.X_full_description[0].name

    @property
    def producer(self) -> str:
        return self.X_producer[0].name

    @property
    def model(self) -> str:
        return self.X_model[0].name

    @property
    def description(self) -> str:
        return self.X_description[0].name

    def fill_load_tests(self, tests: list[LoadTest]):
        self.load_tests = tests


class Contact(BaseModel):
    id: int
    name: str = Field(alias="שם")
    phone: str = Field(alias="טלפון")
    stationary_phone: str = Field(alias="טלפון נייח")
    fax: str = Field(alias="פקס")
    email: str = Field(alias="מייל")
    X_cname: list[BaseRecord] = Field(alias="חברה")
    X_address: list[BaseRecord] = Field(alias="כתובת")
    X_city: list[BaseRecord] = Field(alias="עיר")

    @property
    def cname(self):
        """The cname property."""
        return self.X_cname[0].name

    @property
    def address(self):
        """The address property."""
        return self.X_address[0].name

    @property
    def city(self):
        """The city property."""
        return self.X_city[0].name


class Defiencie(BaseModel):
    topic: str = Field(alias="נושא")
    full: str = Field(alias="פירוט")
    is_repeating: bool = Field(alias="הערה חוזרת")


@dataclass
class Survey:
    id: int
    survey_data: SurveyRecord
    contact: Contact
    machines: list[MachineInstance]
    comments: list[str]
    defiencies: list[Defiencie]
