from baserow_models import Survey
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
                    raise Exception(
                        "preview failed"
                    )  # TODO: add catch and route to broke preview page

                return (await response.json())["url"]

    def _get_paylodad(self, record: Survey):
        return {"company": record}
