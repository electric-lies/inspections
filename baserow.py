from dataclasses import dataclass
from baserow_models import Machine, SurveyRecord, Survey, Contact, SurveyStatus
import logging
import requests
from pydantic import ValidationError
import aiohttp

logging.basicConfig(format="[%(asctime)s]/%(levelname)s - %(message)s",level=logging.DEBUG)

@dataclass()
class BaserowIDs:
    survey_table_id: int
    contact_table_id: int
    machine_table_id: int


class Baserow:
    def __init__(
        self,
        token: str,
        db_id: int,
        ids: BaserowIDs,
        ip: str,
    ):
        self.token = token
        self.db_id = db_id
        self.survey_table = ids.survey_table_id
        self.contact_table = ids.contact_table_id
        self.machine_table = ids.machine_table_id
        self.ip = ip

    def _url(self, table: int, record_id: int = -1) -> str:
        if record_id > 0:
            rid = f"{record_id}/"
        else:
            rid = ""
        return f"http://{self.ip}/api/database/rows/table/{table}/{rid}?user_field_names=true"

    async def duplicate_record(self, record_id) -> int:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Token {self.token}"}
        ) as session:
            async with session.get(
                self._url(self.survey_table, record_id)
            ) as get_response:
                record = SurveyRecord.model_validate_json(await get_response.text())
                #new_record = {key: res[key]['id'] for key in ['תוקף','איש קשר','בוחן','סוג בדיקה','מכונת הרמה','ליקויים']}
                new_record = {
                        'תוקף': 'פתוח',
                        'איש קשר': [record.contact.name],
                        'בוחן': [record.inspector.name],
                        'סוג בדיקה': record.type.name,
                        'מכונת הרמה': [record.machine.name]
                        }
                
            async with session.post(
                self._url(self.survey_table), data=new_record
            ) as set_response:
                if set_response.status != 200:
                    logging.error(
                        f"Duplication of survey record number {record_id} \
                                  failed with status code {set_response.status} and response {await set_response.text()} \
                                  while trying to post {new_record}"
                    )
                    raise Exception("Duplication failed")
                else:
                    logging.info(f"Survey record {record_id} duplicated")
                    return (await set_response.json())['id']

    async def get_record(self, record_id: int) -> Survey | None:
        url = self._url(self.survey_table, record_id)
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
            async with session.get(
                self._url(self.contact_table, cid),
                headers={"Authorization": f"Token {self.token}"},
            ) as response:
                res = await response.text()
        return Contact.model_validate_json(res)

    async def _get_machine(self, mid: int) -> Machine:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._url(self.machine_table, mid),
                    headers={"Authorization": f"Token {self.token}"},
                ) as response:
                    res = await response.text()
            return Machine.model_validate_json(res)
        except ValidationError as err:
            url = (self._url(self.machine_table, mid),)
            logging.error(
                    f"Error during Baserow response parsing from GET {url} with {res=}", #type: ignore
                err,
            )
            raise Exception("Getting machine from baserow failed")

    async def _complete_record(self, record: SurveyRecord) -> Survey:
        contact = self._get_contact(record.contact.id)
        machine = self._get_machine(record.machine.id)
        return Survey(record.id, await contact, await machine)
