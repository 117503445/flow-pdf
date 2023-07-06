import os
import json
import common  # type: ignore
from common import version
from worker import Executer, ExecuterConfig, workers_prod  # type: ignore
from pathlib import Path
from htutil import file
import shutil

logger = common.create_main_logger()
logger.info(f"version: {version}")

eventsStr = os.getenv("FC_CUSTOM_CONTAINER_EVENT")

if not eventsStr:
    logger.error("FC_CUSTOM_CONTAINER_EVENT is not set")
    exit(1)

# example event

# {
#     "events": [
#         {
#             "eventName": "ObjectCreated:PutObject",
#             "eventSource": "acs:oss",
#             "eventTime": "2023-06-09T06:08:58.000Z",
#             "eventVersion": "1.0",
#             "oss": {
#                 "bucket": {
#                     "arn": "acs:oss:cn-hangzhou:1035038953803932:flow-pdf",
#                     "name": "flow-pdf",
#                     "ownerIdentity": "1035038953803932",
#                     "virtualBucket": ""
#                 },
#                 "object": {
#                     "deltaSize": 184292,
#                     "eTag": "D56D71ECADF2137BE09D8B1D35C6C042",
#                     "key": "input/bitcoin.pdf",
#                     "objectMeta": {
#                         "mimeType": "application/pdf"
#                     },
#                     "size": 184292
#                 },
#                 "ossSchemaVersion": "1.0",
#                 "ruleId": "214f3eaf7f78626cd6279dae3cf63dde54297412"
#             },
#             "region": "cn-hangzhou",
#             "requestParameters": {
#                 "sourceIPAddress": "125.120.47.179"
#             },
#             "responseElements": {
#                 "requestId": "6482C1F953726E373581D661"
#             },
#             "userIdentity": {
#                 "principalId": "276882140338155176"
#             }
#         }
#     ]
# }

events: dict = json.loads(eventsStr)["events"]
if len(events) == 0:
    logger.error("events is empty")
    exit(1)

dir_data = Path("/data")
dir_input = dir_data / "input"
dir_output = dir_data / "output"
dir_input.mkdir(parents=True, exist_ok=True)
dir_output.mkdir(parents=True, exist_ok=True)

for event in events:
    file_k: str = event["oss"]["object"]["key"]
    stem = Path(file_k).stem

    file_task = dir_output / stem / "task.json"
    file_doc = dir_output / stem / "doc.json"

    if file_doc.exists():
        doc = file.read_json(file_doc)
        if doc["meta"]["flow-pdf-version"] == version:
            continue
        else:
            logger.info(f'clean old version {doc["meta"]["flow-pdf-version"]}')
            shutil.rmtree(dir_output / stem)

    file_input = dir_input / f'{stem}.pdf'

    logger.info(f"start {file_input.name}")

    file.write_json(file_task, {"status": "executing"})

    cfg = ExecuterConfig(version, False)  # type: ignore
    e = Executer(file_input, dir_output / stem, cfg)
    e.register(workers_prod)
    try:
        e.execute()

        file.write_json(file_task, {"status": "done"})

    except Exception as e:
        logger.error(e)

        file.write_json(
            file_task,
            {
                "status": "error",
                "error": str(e),
            },
        )

        continue

    logger.info(f"end {file_input.name}")
