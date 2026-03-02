# Misfold-Spotter: Protein Misfolding Detection Pipeline

Multi-agent system for detecting protein misfolding from amino acid sequences.

## Architecture

| Agent | Role | Model |
|-------|------|-------|
| Agent 1 - The Mapper | Anomaly detection via ProstT5 3Di translation | Facebook/ESM2 |
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

## Foldseek Binary Requirement (Important)

`foldseek/bin/foldseek` is tracked with Git LFS. If LFS objects are not pulled, that file will be a small text pointer instead of the real executable, and Agent 1 will fail during 3Di conversion. Note that the current foldseek binaries support only MacOS. A separate installation needs to be carried out for Linux. Windows users may test our project on WSL. 

### One-time setup

```bash
git lfs install
git lfs pull
```

If `foldseek` is managed as a nested repo, run LFS pull there as well:

```bash
cd foldseek
git lfs pull
```

### Verify

```bash
ls -lh foldseek/bin/foldseek
file foldseek/bin/foldseek
```

Expected: a large file (hundreds of MB) reported as an ELF executable, not ASCII text.
