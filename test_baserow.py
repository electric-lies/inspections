import asyncio
import concurrent.futures

from baserow import Baserow

pool = concurrent.futures.ThreadPoolExecutor()

b = Baserow(
    token="LXAPUwIs9yCmQMBIKxKRVZgBWU8H1U6T",
    db_id=2,
    survey_table_id=8,
    contact_table_id=4,
    ip="35.210.117.126"
)
result = pool.submit(asyncio.run, b.get_record(1)).result()
print(result)
