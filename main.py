import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, ValidationError
import requests
import os

class Update(BaseModel):
    table_id: int
    event_type: str
    event_id: str
    items: list[dict]


class ProjectRecord(BaseModel):
    id: int


app = FastAPI()

IP = os.environ.get("OWN_IP", "localhost") # env var in prod, localhost in dev
if IP == "localhost":
    logging.warning('"OWN_IP" env var is missing, running in dev mode')
# Baserow
TOKEN = os.environ["BASEROW_TOKEN"] # TODO: find solution for dev
DB_ID = 2
PROJECT_TABLE_ID = 8
BASEROW_IP = os.environ.get("BASEROW_IP", "localhost") # env var in prod, localhost in dev 
if IP == "localhost":
    logging.warning('"BASEROW_IP" env var is missing, running in dev mode')

# Documint
DOC_TOKEN =TOKEN = os.environ["DOCUMINT_TOKEN"]
TEMPLATE_ID = TOKEN = os.environ["DOCUMINT_TEMPLATE_ID"]

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


@app.post("/updates")
async def updateController(update: Update):
    logging.warning(update.model_dump_json())
    return {"message": "got update"}


async def get_record(id: int) -> ProjectRecord | None:
    url = f"http://{BASEROW_IP}/api/database/rows/table/{PROJECT_TABLE_ID}/{id}/?user_field_names=true"
    res = requests.get(
       url,
        headers={"Authorization": f"Token {TOKEN}"},
    )
    try:
        record = ProjectRecord.model_validate_json(res.text)
    except ValidationError as err:
        logging.error(f"Error during Baserow response parsing from GET {url} with {res.text=}", err)
        return None

    return record


async def generate_preview(record: ProjectRecord):
    # get_template_for_backup_url = (
    #     f"https://api.documint.me/1/templates/{TEMPLATE_ID}?select"
    # )
    merge_url = f"https://api.documint.me/1/templates/{TEMPLATE_ID}/content?preview=true&active=true"

    payload = {"company": record.id}
    headers = {"api_key": DOC_TOKEN}

    response = requests.request("POST", merge_url, headers=headers, data=payload)
    if response.status_code != 200:
        print(response.text)
        return f"{IP}/broken_preview"
    return response.json()["url"]


@app.get("/preview/{row_id}")
async def preview(row_id):
    record = await get_record(row_id)
    if record is None:
        return RedirectResponse(f"{IP}/broken_preview")
    url = await generate_preview(record)
    return RedirectResponse(url)


@app.get("/broken_preview")
async def broken_preview():
    return HTMLResponse(
        """<html>
        <head>
            <title>Oops!</title>
        </head>
        <body>
            <h1>Preview run into some problem, call illay, he will sort it out</h1>
        </body>
    </html>"""
    )


@app.get("/button/{row_id}")
async def root(row_id):
    res = requests.patch(
        f"http://{BASEROW_IP}/api/database/rows/table/{PROJECT_TABLE_ID}/{row_id}/?user_field_names=true",
        headers={"Authorization": f"Token {TOKEN}", "Content-Type": "application/json"},
        json={"Name": "auto", "Last name": "change", "Notes": "here", "Active": True},
    )
    return HTMLResponse(
        """<html>
        <head>
            <title>Autoclose page</title>
        </head>
        <body>
            <h1>If you see that contact illay (tell him auto close stopped working)</h1>
        </body>
    </html>
    """,
        status_code=500,
    )
