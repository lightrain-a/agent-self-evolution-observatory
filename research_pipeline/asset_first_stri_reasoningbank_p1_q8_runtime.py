"""Q8 bounded Docker-start acknowledgement grace."""

from research_pipeline.asset_first_stri_reasoningbank_p1_q7_runtime import (
    GracefulReconciledDockerRun,
)

Q8_CONTRACT_SHA256 = "7d3046b26245f612e96807574903249b6550caacd5fa7b3156aba51e57ed0d81"


class StartGraceDockerRun(GracefulReconciledDockerRun):
    ACK_CONTRACT_SHA256 = Q8_CONTRACT_SHA256
    START_TIMEOUT_SECONDS = 180
