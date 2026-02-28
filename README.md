# Misfold-Spotter: Protein Misfolding Detection Pipeline

Multi-agent system for detecting protein misfolding from amino acid sequences.

## Architecture

| Agent | Role | Model |
|-------|------|-------|
| Agent 1 - The Mapper | Anomaly detection via ProstT5 3Di translation | Rostlab/ProstT5 |
| **Agent 2 - The Specialist** | Severity classification of structural anomalies | ministral-14b-latest |
| Agent 3 - The Orchestrator | Synthesize findings into human-readable reports | Mistral Large |

## Agent 2: The Specialist (Severity Classifier)

Takes 3Di structural sequences (from Agent 1) and classifies the severity of detected anomalies using thermodynamic stability analysis grounded in the Rocklin MegaScale dataset.

### Output Schema

```json
{
  "severity_label": "Low Risk | Moderate Risk | High Risk of Destabilization",
  "confidence": 0.95,
  "estimated_ddG_impact": 1.8,
  "structural_features": {
    "helix_fraction": 0.375,
    "strand_fraction": 0.125,
    "coil_fraction": 0.5,
    "disorder_fraction": 0.333,
    "core_contact_density": 0.25
  },
  "risk_factors": ["..."],
  "summary": "One-sentence clinical-style summary"
}
```

### Integration with Agent 1 and Agent 3

Agent 2 receives input from Agent 1 (The Mapper) and passes output to Agent 3 (The Orchestrator):

```python
# Agent 1 output -> Agent 2 input
mapper_output = {
    "sequence_3di": "dvvlddnnsqqsnn...",
    "anomaly_z_score": 2.1
}

# Agent 2 processing
result = classifier.classify(**mapper_output)

# Agent 2 output -> Agent 3 input
agent3_input = {
    "severity_label": result.severity_label,
    "confidence": result.confidence,
    "analysis": result.to_dict()
}
```
