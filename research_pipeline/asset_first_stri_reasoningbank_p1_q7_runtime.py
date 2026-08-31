"""Q7 bounded read-only create acknowledgement grace."""

from research_pipeline.asset_first_stri_reasoningbank_p1_q6_runtime import (
    ReconciledDockerRun,
)

Q7_CONTRACT_SHA256 = "4794b712a5f4dd66511b1c37d221bc19d893c9b3e2745089c150e0095b94e5e8"


class GracefulReconciledDockerRun(ReconciledDockerRun):
    ACK_CONTRACT_SHA256 = Q7_CONTRACT_SHA256
    INSPECT_TIMEOUT_SECONDS = 180
