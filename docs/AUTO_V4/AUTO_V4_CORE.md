# AUTO_V4_CORE

## Ucel

Definovat jadro systemu, ktere koordinuje datovy tok mezi moduly bez implementace konkretniho downloaderu, parseru, GUI nebo generatoru.

## Odpovednost

- Drzi orchestrace mezi moduly.
- Definuje stav zpracovani auta.
- Zajistuje, ze modulove hranice zustanou ciste.
- Nevlastni specializovanou logiku jednotlivych modulu.

## Vstupy

- `Car`,
- market report,
- openlane source record,
- konfigurace systemu,
- validacni reporty,
- uzivatelske rozhodnuti o dalsim kroku.

## Vystupy

- stav zpracovani,
- seznam dalsich potrebnych kroku,
- orchestrace pipeline,
- auditni zaznam rozhodnuti.

## Verejne API

- `create_workflow(entity_id, workflow_type)`
- `get_workflow_status(workflow_id)`
- `advance_workflow(workflow_id, action)`
- `list_next_actions(entity_id)`
- `record_decision(entity_id, decision)`

## Datove struktury

```text
Workflow
  id
  entityId
  workflowType
  status
  currentStep
  requiredInputs
  completedSteps
  blockedBy

WorkflowDecision
  id
  entityId
  decision
  reason
  createdAt
  createdBy
```

## Zavislosti

- `AUTO_V4_STANDARD.md`
- `CAR_DATA_MODEL.md`
- `OPENLANE_ENGINE.md`
- `MARKET_ENGINE.md`
- `REPORT_ENGINE.md`
- `TESTING_STANDARD.md`

## Poradi implementace

1. Definovat stavy workflow.
2. Definovat udalosti a rozhodnuti.
3. Napojit validaci dat.
4. Napojit market a report moduly.
5. Pozdeji napojit downloader, parser a publikaci.

