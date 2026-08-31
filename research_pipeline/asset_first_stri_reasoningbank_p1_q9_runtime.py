"""Q9 600-second Docker-start acknowledgement grace."""

from research_pipeline.asset_first_stri_reasoningbank_p1_q8_runtime import StartGraceDockerRun

Q9_CONTRACT_SHA256 = "5779bd037811c6446610eb31b6b7f73f8110993f5ad0f112902523477ee0158b"


class ExtendedStartGraceDockerRun(StartGraceDockerRun):
    ACK_CONTRACT_SHA256 = Q9_CONTRACT_SHA256
    START_TIMEOUT_SECONDS = 600
