"""Custom G1 velocity task with easier training settings."""
import math
from mjlab.tasks.velocity.config.g1.env_cfgs import unitree_g1_flat_env_cfg
from mjlab.tasks.velocity.config.g1.rl_cfg import unitree_g1_ppo_runner_cfg
from mjlab.tasks.registry import register_mjlab_task
def custom_g1_flat_env_cfg(play: bool = False):
    cfg = unitree_g1_flat_env_cfg(play=play)
    cfg.terminations["fell_over"].params["limit_angle"] = math.radians(80.0)
    if "push_robot" in cfg.events:
        del cfg.events["push_robot"]
    cfg.rewards["upright"].weight = 20.0
    cfg.rewards["foot_clearance"].weight = -0.1
    cfg.rewards["foot_swing_height"].weight = -0.01
    cfg.rewards["action_rate_l2"].weight = -0.001
    cfg.rewards["angular_momentum"].weight = -0.005
    cfg.rewards["body_ang_vel"].weight = -0.01
    cfg.rewards["dof_pos_limits"].weight = -0.1
    if "command_vel" in cfg.curriculum:
        cfg.curriculum["command_vel"].params["velocity_stages"] = [
            {"step": 0, "lin_vel_x": (0.0, 0.2), "lin_vel_y": (0.0, 0.0), "ang_vel_z": (0.0, 0.0)},
            {"step": 200000, "lin_vel_x": (0.0, 0.4), "lin_vel_y": (0.0, 0.0), "ang_vel_z": (0.0, 0.1)},
            {"step": 400000, "lin_vel_x": (0.0, 0.7), "lin_vel_y": (0.0, 0.0), "ang_vel_z": (-0.2, 0.2)},
            {"step": 600000, "lin_vel_x": (-1.0, 1.0), "lin_vel_y": (-0.5, 0.5), "ang_vel_z": (-0.5, 0.5)},
        ]
    return cfg
register_mjlab_task(
    task_id="Custom-Velocity-Flat-Unitree-G1",
    env_cfg=custom_g1_flat_env_cfg(play=False),
    play_env_cfg=custom_g1_flat_env_cfg(play=True),
    rl_cfg=unitree_g1_ppo_runner_cfg(),
)
