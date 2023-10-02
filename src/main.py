import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import requests
import os
from .baserow import Baserow, BaserowIDs
from .documint import Documint


class Update(BaseModel):
    table_id: int
    event_type: str
    event_id: str
    items: list[dict]


app = FastAPI()

IP = os.environ.get("OWN_IP", "localhost")  # env var in prod, localhost in dev
if IP == "localhost":
    logging.warning('"OWN_IP" env var is missing, running in dev mode')
# Baserow
TOKEN = os.environ["BASEROW_TOKEN"]  # TODO: find solution for dev
DB_ID = 2
BASEROW_IP = os.environ.get(
    "BASEROW_IP", "localhost"
)  # env var in prod, localhost in dev
if IP == "localhost":
    logging.warning('"BASEROW_IP" env var is missing, running in dev mode')

ids = BaserowIDs(8, 4, 9)

b = Baserow(token=TOKEN, db_id=DB_ID, ids=ids, ip=BASEROW_IP)


# Documint
DOC_TOKEN = TOKEN = os.environ["DOCUMINT_TOKEN"]
TEMPLATE_ID = TOKEN = os.environ["DOCUMINT_TEMPLATE_ID"]

d = Documint(DOC_TOKEN, TEMPLATE_ID)

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


@app.post("/updates")
async def updateController(update: Update):
    logging.warning(update.model_dump_json())
    return {"message": "got update"}


@app.get("/duplicate/{row_id}")
async def duplicate(row_id: int):
    new_row_id = await b.duplicate_record(row_id)
    return RedirectResponse(
        f"http://{BASEROW_IP}/database/{DB_ID}/table/{ids.survey_table_id}/row/{new_row_id}"
    )


@app.get("/preview/{row_id}")
async def preview(row_id):
    try:
        return RedirectResponse(await d.generate_preview(await b.get_record(row_id)))
    except Exception:
        return RedirectResponse("{IP}/broken_preview")


@app.get("/broken_preview")
async def broken_preview():
    return HTMLResponse(
        """<html>
        <head>
            <title>Oops!</title>
        </head>
        <body>
            <h1>Preview run into some problem, call illay, he will sort it out :)</h1>
        </body>
    </html>"""
    )


# depricated
@app.get("/button/{row_id}")
async def root(row_id):
    res = requests.patch(
        f"http://{BASEROW_IP}/api/database/rows/table/{id.table_id}/{row_id}/?user_field_names=true",
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
