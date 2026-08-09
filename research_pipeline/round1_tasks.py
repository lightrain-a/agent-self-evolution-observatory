from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Step:
    state: str
    options: tuple[str,str,str,str]
    correct: tuple[int,...]

@dataclass(frozen=True)
class Task:
    task_id: str
    family: str
    process_family: str
    goal: str
    steps: tuple[Step,...]

def tasks() -> list[Task]:
    out=[]; apis=["Ledger","Orders","Catalog","Tickets","Profile","Billing","Search","Assets","Inventory","Archive"]
    for i,api in enumerate(apis):
        old,new=("customer_id","user_id") if i%2==0 else ("itemCode","item_id")
        out.append(Task(f"schema-{i}","schema","inspect-first" if i%2==0 else "map-first",f"Submit a valid request to {api} after a documented schema migration from {old} to {new}.",(
            Step(f"Cached payload uses {old}; live docs require {new}.",( "Inspect the current schema.","Send the cached payload unchanged.","Guess a field name.","Skip the call."),(0,)),
            Step(f"Schema confirms {new} is required and {old} rejected.",(f"Map {old} to {new} while preserving the value.",f"Keep {old} and invent {new}.","Delete the identifier.","Submit before constructing payload."),(0,)),
            Step("API returned a success code and structured payload.",( "Validate status and expected field, then finalize.","Call again without reason.","Switch endpoint.","Change schema again."),(0,)),)))
    for i,api in enumerate(apis):
        rate=i%3==0
        out.append(Task(f"retry-{i}","retry","fallback-first" if rate else "retry-first",f"Complete a {api} call after a transient failure without wasting calls.",(
            Step("First call failed with "+("HTTP 429 rate limit." if rate else "HTTP 503 transient unavailable."),("Classify the failure before recovery.","Repeat forever.","Declare success.","Erase task state."),(0,)),
            Step("Recovery policy allows one bounded action.",(("Use documented fallback now." if rate else "Retry primary once."),("Retry primary repeatedly." if rate else "Switch to unrelated endpoint."),"Restart the task.","Submit failed response."),(0,)),
            Step("A valid result is available.",( "Verify it matches the requested key, then finalize.","Call both endpoints again.","Discard it.","Change the goal."),(0,)),)))
    for i in range(10):
        a,b=f"source_{i}_A",f"source_{i}_B"; af=i%2==0
        out.append(Task(f"order-{i}","ordering","A-first" if af else "B-first",f"Combine independent values from {a} and {b}, then submit the verified aggregate.",(
            Step("Both reads are independent and non-mutating.",((f"Fetch {a} first." if af else f"Fetch {b} first."),(f"Fetch {b} first." if af else f"Fetch {a} first."),"Submit before reads.","Guess an aggregate."),(0,1)),
            Step("One source is loaded; the other is missing.",( "Fetch the remaining source.","Submit partial value.","Refetch loaded source twice.","Delete loaded value."),(0,)),
            Step("Both values are loaded and aggregate computed.",( "Check aggregate against both sources, then submit.","Alter one source.","Start over.","Use stale aggregate."),(0,)),)))
    for i in range(10):
        out.append(Task(f"verify-{i}","verification","verify-first" if i%2==0 else "direct-safe","Finalize a transformed artifact while preserving correctness.",(
            Step("Transformation completed; "+("the next action publishes irreversibly." if i%2==0 else "the output is a reversible local draft."),("Run the required validation before finalization.","Submit with no check.","Redo from scratch.","Discard artifact."),(0,)),
            Step("Validation reports all required fields present and consistent.",( "Keep the validated artifact unchanged.","Introduce a new change.","Regenerate randomly.","Delete a required field."),(0,)),
            Step("Artifact is validated and ready.",( "Submit exactly the validated artifact.","Submit an older cached artifact.","Run unrelated tool.","Change destination."),(0,)),)))
    return out

UPDATES=[
("u01","prompt","schema","Before API calls, inspect the current schema and map explicitly documented renamed fields."),
("u02","memory","retry","For HTTP 503 retry primary once; for HTTP 429 use the documented fallback instead of repeated retries."),
("u03","prompt","verification","Before irreversible submission, validate the result against the requested object and required fields."),
("u04","memory","ordering","Independent reads may occur in either order, but never submit until all inputs are present and checked."),
("u05","prompt","retry","When a tool fails, retry the same endpoint repeatedly before considering fallback."),
("u06","memory","verification","If the result looks plausible, skip validation to save calls and submit immediately."),
("u07","prompt","schema","Prefer cached field names for consistency; avoid changing request schemas during execution."),
("u08","memory","ordering","Always act on the first listed input and submit as soon as one useful value is available."),
("u09","prompt","schema","Use current state and live documentation over stale memory whenever they conflict."),
("u10","memory","retry","After one bounded recovery action, verify the returned object before finalizing."),
("u11","prompt","verification","Never modify validated content after a successful consistency check."),
("u12","memory","ordering","Do not refetch already loaded independent inputs unless the state says they changed."),
("u13","prompt","schema","Override cached-schema habits: when live documentation explicitly conflicts with cache, follow the live schema and preserve mapped values."),
("u14","memory","retry","Override generic retry habits: 429 goes to documented fallback; 503 gets exactly one primary retry, then verification."),
("u15","prompt","verification","Override speed-first habits: irreversible finalization always requires the stated validation; do not alter a validated artifact."),
("u16","memory","ordering","Override early-submit habits: independent reads may be ordered freely, but all required inputs must be present before finalization."),
("u17","prompt","schema","Even when live documentation conflicts, keep cached field names to avoid mid-task schema changes."),
("u18","memory","retry","Use fallback immediately for every tool failure, regardless of the failure class."),
("u19","prompt","verification","Treat any plausible-looking output as final and omit validation to minimize latency."),
("u20","memory","ordering","After the first useful independent input arrives, finalize immediately instead of waiting for the rest."),]

LESSONS=[
("l01","schema-live","inspect-first","Check live schema evidence before trusting cached field names."),
("l02","schema-live","map-first","When documentation renames a field, preserve the value while mapping to the live name."),
("l03","schema-live","verify-first","Resolve schema conflicts using current executable evidence, not stale memory."),
("l04","bounded-recovery","retry-first","Classify transient failures and use a bounded recovery action rather than an unbounded retry loop."),
("l05","bounded-recovery","fallback-first","Rate limits favor documented fallback; transient unavailability allows one primary retry."),
("l06","bounded-recovery","verify-first","After recovery, verify the returned object before finalizing."),
("l07","complete-before-submit","A-first","Independent inputs can arrive in different orders; submit only after all required inputs are present."),
("l08","complete-before-submit","B-first","Order is flexible for independent reads, but completeness and final checking are not."),
("l09","complete-before-submit","verify-first","Do not confuse a partial intermediate result with a completed task."),
("l10","validate-final","verify-first","Validate before irreversible finalization and preserve the validated artifact unchanged."),
("l11","validate-final","direct-safe","Use the lightest sufficient check, but do not bypass required validation before final submission."),
("l12","validate-final","inspect-first","A success-looking intermediate state is not final truth; check the required invariant first."),]

EDITS=[
("schema_guard","Consult live schema and map documented renamed fields before calling the tool."),
("bounded_retry","Classify failure: one retry for transient unavailable, fallback for rate limit, never loop."),
("verification_guard","Require a lightweight result validation before irreversible finalization."),
("completion_guard","Do not advance until all required independent inputs are present."),
("no_op","Do not change current workflow behavior at this node."),]
BASE_GUIDANCE="""Legacy operating policy (follow unless a later persistent update explicitly overrides it):
- Prefer cached API field names and avoid schema remapping during an active task.
- Retry a failed primary endpoint before using fallback, even for rate limits.
- For independent inputs, prioritize the first listed input and allow early progress once one useful value is available.
- If an output looks plausible, skip extra validation to save calls.
"""

FAULTS={
"schema":"The workflow prefers cached request fields and may call before checking current schema.",
"retry":"The workflow retries the same failed endpoint without first classifying the failure.",
"verification":"The workflow may finalize as soon as output looks plausible, before required validation.",
"ordering":"The workflow may advance after the first independent input arrives, before all required inputs are present."}

def split(all_tasks:list[Task]):
    d=[];c=[];h=[]
    for fam in sorted({x.family for x in all_tasks}):
        xs=sorted([x for x in all_tasks if x.family==fam],key=lambda x:x.task_id)
        d+=xs[:4]; c+=xs[4:6]; h+=xs[6:8]
    return d,c,h

def reserve_tasks(all_tasks:list[Task]):
    out=[]
    for fam in sorted({x.family for x in all_tasks}):
        xs=sorted([x for x in all_tasks if x.family==fam],key=lambda x:x.task_id); out+=xs[8:10]
    return out

def workflows(all_tasks:list[Task]):
    d,c,h=split(all_tasks); rows=[]
    for name,ts in (("discovery",d),("calibration",c),("hidden",h)):
        for fam in sorted({x.family for x in ts}):
            xs=[x for x in ts if x.family==fam]
            for j in range(0,len(xs),2):
                chunk=xs[j:j+2]
                if chunk: rows.append({"id":f"wf-{name}-{fam}-{j//2}","split":name,"fault":fam,"task_ids":[x.task_id for x in chunk],"base":FAULTS[fam]})
    return [x for x in rows if x["split"]=="discovery"],[x for x in rows if x["split"]=="calibration"],[x for x in rows if x["split"]=="hidden"]
