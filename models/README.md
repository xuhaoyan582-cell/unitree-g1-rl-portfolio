# Retained exported policy

`policy_lstm_1.pt` is the retained TorchScript recurrent policy exported during the project's Unitree RL GYM workflow. The model has 47 observation inputs, an LSTM with 64 hidden units, a 32-unit actor layer, and 12 action outputs.

The historical project record describes loading `model_5950.pt` and exporting this policy before the MuJoCo replay. The original training checkpoint was not recovered and is not included, so it cannot be independently compared with this retained export. This file is provided as a project artifact, not as a full training-reproduction package or a physical-robot deployment recommendation.

- File size: 144,596 bytes
- SHA-256: `a1aaa549c601c6aaf6b448038b96abaabc4065f21ed8ed73235f7c6b5080a37f`
- No new model licence has been selected or applied. The upstream framework and any applicable third-party terms remain as described in [the notices](../THIRD_PARTY_NOTICES.md).
