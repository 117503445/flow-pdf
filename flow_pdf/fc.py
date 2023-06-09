import os
import json
import common  # type: ignore
from common import version
import oss2
from worker import Executer, ExecuterConfig, workers_prod  # type: ignore
from pathlib import Path

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

events: dict = json.loads(eventsStr)
dir_input = Path("/tmp") / "input"
dir_input.mkdir(parents=True, exist_ok=True)

for event in events["events"]:
    auth = oss2.Auth(os.getenv("ak"), os.getenv("sk"))
    bucket = oss2.Bucket(auth, os.getenv("endpoint"), event["oss"]["bucket"]["name"])

    file_k = event["oss"]["object"]["key"]

    file_input = dir_input / os.path.basename(file_k)

    bucket.get_object_to_file(file_k, file_input)

    dir_output: Path = Path("/tmp") / "output" / os.path.basename(file_k)
    dir_output.mkdir(parents=True, exist_ok=True)

    logger.info(f"start {file_input.name}")
    cfg = ExecuterConfig(version, False)  # type: ignore
    e = Executer(file_input, dir_output, cfg)
    e.register(workers_prod)
    e.execute()
    logger.info(f"end {file_input.name}")

    # upload files to oss, rescursive
    for file in dir_output.glob("**/*"):
        if file.is_file():
            oss_key = (
                f"output/{os.path.basename(file_k)}/{file.relative_to(dir_output)}"
            )
            logger.info(f"upload, oss_key = {oss_key}, file = {file}")

            bucket.put_object_from_file(oss_key, str(file))
