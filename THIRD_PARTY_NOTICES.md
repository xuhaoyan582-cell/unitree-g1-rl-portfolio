# Third-party notices

## Unitree RL GYM

Upstream: https://github.com/unitreerobotics/unitree_rl_gym

The snapshots `code/unitree_rl_gym/g1_config.py` and `g1.yaml` originate from Unitree RL GYM. Their implementation/configuration contents are retained; attribution comments were added for this portfolio. `record_video.py` is a project adaptation of `deploy/deploy_mujoco/deploy_mujoco.py`, adding headless EGL recording, a policy-path override, and recording controls. These upstream-derived portions are subject to the [original BSD 3-Clause licence](licenses/UNITREE_RL_GYM_BSD_3_CLAUSE.txt), reproduced from the official upstream LICENSE. No copyright notices were removed.

The files are presented as selected snapshots and do not claim that Unitree's framework, PPO implementation, or standard G1 configuration was authored by Haoyan Xu.

## Other frameworks

The historical `g1_custom.py` imports mjlab APIs. mjlab is available at https://github.com/mujocolab/mjlab under Apache-2.0; no mjlab implementation is included in this repository. Refer to its upstream licence when obtaining the dependency.

Unitree RL GYM also builds on legged_gym, rsl_rl, MuJoCo, and Unitree SDK components. Those dependencies and robot asset packages are not redistributed here. Their respective upstream terms apply when obtaining them separately.

## Portfolio material

The project narrative, selected run excerpt, and demonstration are provided for reviewing this student's placement work. No additional repository-wide open-source licence has been selected for the student's original material. No new model licence has been assigned to the retained exported policy. The upstream BSD licence applies to its identified upstream-derived code, not automatically to the entire portfolio.
