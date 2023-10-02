from .baserow_models import Survey
import aiohttp


class Documint:
    def __init__(self, doc_token: str, template_id: str) -> None:
        self.merge_url = (
            f"https://api.documint.me/1/templates/{template_id}/content?preview=true"
        )
        self.doc_token = doc_token

    async def generate_preview(self, record: Survey):
        # get_template_for_backup_url = (
        #     f"https://api.documint.me/1/templates/{TEMPLATE_ID}?select"
        # )
        async with aiohttp.ClientSession(
            headers={"api_key": self.doc_token}
        ) as session:
            async with session.post(
                self.merge_url, data=self._get_paylodad(record)
            ) as response:
                if response.status != 200:
                    print(response.text)
                    raise Exception("preview failed")

                return (await response.json())["url"]

    def _check_boxes(self, record: Survey) -> dict:
        var = record.survey_data.type.name
        return {
            "checkbox1": var == "ראשונית",
            "checkbox2": var == "תקפותית",
            "checkbox3": var == "לאחר תיקון",
            "checkbox4": var == "לאחר שינוי",
        }

    def _get_paylodad(self, record: Survey):
        return {
            "survey_num": record.id,
            "current_test_date": record.survey_data.creation_date,
            "next_test_date": record.survey_data.next_date,
            "last_test_date": record.survey_data.previous_test_date,
            "last_test_num": record.survey_data.previous_test_id,
            "test_done_by": record.survey_data.previous_test_inspector,  # last test
            "contact": record.contact.name,
            "company_name": record.contact.cname,
            "telephone_num": record.contact.phone,
            "fax": record.contact.fax,
            "phone_num": "?",  # TODO
            "e-mail": record.contact.email,
            "postal_code": "?",  # TODO
            "address": record.contact.address,
            "city": record.contact.city,
            "description_of_machine": record.machines[0].description,
            # title machine details
            **self._check_boxes(record),
            "num_of_row": [
                {
                    "work_load": [test.safe_load for test in machine.load_tests],
                    "load_radius": [test.radius for test in machine.load_tests],
                    "test_load": [test.tested_load for test in machine.load_tests],
                    "inside_num": machine.inner_number,
                    "Serial_num": machine.serial_number,
                    "model": machine.model,
                    "manufacturer": machine.producer,
                    "description": machine.description,  # or full?
                    "num_of_row": i,
                }
                for i, machine in enumerate(record.machines)
            ],
            "note_chekbox": [],
            "note_detail": [{"note_detail": "1"}],
            "note_subject": [{"note_subject": "1"}],
            "note_num": [{"note_num": "1"}],
            "images": [{"url": ""}],
        }
