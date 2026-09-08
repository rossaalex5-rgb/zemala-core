# ZEMALA // LOCAL-FIRST SMART HOME

## PRIMARY USE CASE

ZEMALA is a Local-First alternative for Smart Home and agentic device control.

The central principle:

> The home keeps its own state.  
> Live AI understands the state and proposes actions.  
> The local Core controls authorization and execution.  
> The resulting state is returned to the system.

## THE LIVE-AI LOOP

SEE / UNDERSTAND
→ current local system state

PROPOSE
→ AI generates a proposed action

AUTHORIZE / EXECUTE
→ the local ZEMALA Core remains the execution authority

RETURN
→ execution result becomes part of the persistent system state

## ARCHITECTURAL POSITION

ZEMALA is designed to reduce dependence on a foreign cloud as the control center.

The persistent state can be versioned and reconstructed independently of a single AI instance.

Git provides versioned state history.
Termux provides local execution and integration.
MCP/A2A or other interfaces may provide communication with tools, agents and devices.

These interfaces are transport mechanisms.
The canonical ZEMALA state remains the reference point.

## IMPORTANT

Do not infer capabilities that are not implemented or independently verified.

Conversation is transient.
State is persistent.
Evidence is traceable.
Contributions are transferable.

## ONE-SENTENCE ENTRY ANCHOR

ZEMALA is a Local-First Smart-Home and agent-control architecture in which the local system keeps its own state and a Live AI can interact with that state without requiring a foreign cloud to be the control center.

O-M-A.
