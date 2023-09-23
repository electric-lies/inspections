from baserow_models import SurveyRecord, Survey, Contact
import logging
import requests
from pydantic import ValidationError
import aiohttp


class Baserow:
    def __init__(
        self,
        token: str,
        db_id: int,
        survey_table_id: int,
        contact_table_id: int,
        ip: str,
    ):
        self.token = token
        self.db_id = db_id
        self.survey_table = survey_table_id
        self.contact_table = contact_table_id
        self.ip = ip

    def url(self, table: int, record_id: int) -> str:
        return f"http://{self.ip}/api/database/rows/table/{table}/{record_id}/?user_field_names=true"

    async def get_record(self, record_id: int) -> Survey | None:
        url = self.url(self.survey_table, record_id)
        res = requests.get(
            url,
            headers={"Authorization": f"Token {self.token}"},
        )
        try:
            record = SurveyRecord.model_validate_json(res.text)
        except ValidationError as err:
            logging.error(
                f"Error during Baserow response parsing from GET {url} with {res.text=}",
                err,
            )
            return None

        survey = await self._complete_record(record)

        return survey

    async def _get_contact(self, cid: int) -> Contact:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url(self.contact_table, cid),headers={"Authorization": f"Token {self.token}"}) as response:
                res = await response.text()
        return Contact.model_validate_json(res)

    async def _complete_record(self, record: SurveyRecord) -> Survey:
        contact = self._get_contact(record.contact.id)

        return Survey(record.id, await contact)
