# Adapted from Unitree RL GYM deploy_mujoco.py for this placement workflow.
# Retained project snapshot; adds headless EGL recording and policy selection.
# Upstream-derived portions: see ../../licenses/UNITREE_RL_GYM_BSD_3_CLAUSE.txt.
"""
Record MuJoCo deployment as MP4 video (headless).
Adapted from deploy_mujoco.py — handles LSTM policy and uses EGL rendering.
"""
import os
os.environ["MUJOCO_GL"] = "egl"  # must set before importing mujoco

import argparse
import numpy as np
import mujoco
import torch
import yaml
import imageio
from legged_gym import LEGGED_GYM_ROOT_DIR


def get_gravity_orientation(quaternion):
    qw, qx, qy, qz = quaternion
    g = np.zeros(3)
    g[0] = 2 * (-qz * qx + qw * qy)
    g[1] = -2 * (qz * qy + qw * qx)
    g[2] = 1 - 2 * (qw * qw + qz * qz)
    return g


def pd_control(target_q, q, kp, target_dq, dq, kd):
    return (target_q - q) * kp + (target_dq - dq) * kd


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="config file in configs/ folder, e.g. g1.yaml")
    parser.add_argument("--policy", type=str, default=None,
                        help="override policy_path from config (use exported LSTM policy)")
    parser.add_argument("--duration", type=float, default=10.0,
                        help="simulation duration in seconds")
    parser.add_argument("--output", type=str, default="g1_walk.mp4",
                        help="output video filename")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--cmd_x", type=float, default=0.5,
                        help="forward velocity command (m/s)")
    args = parser.parse_args()

    # ---------- Load config ----------
    cfg_path = f"{LEGGED_GYM_ROOT_DIR}/deploy/deploy_mujoco/configs/{args.config_file}"
    with open(cfg_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    policy_path = args.policy if args.policy else \
        config["policy_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)
    xml_path = config["xml_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)

    simulation_dt = config["simulation_dt"]
    control_decimation = config["control_decimation"]
    kps = np.array(config["kps"], dtype=np.float32)
    kds = np.array(config["kds"], dtype=np.float32)
    default_angles = np.array(config["default_angles"], dtype=np.float32)
    ang_vel_scale = config["ang_vel_scale"]
    dof_pos_scale = config["dof_pos_scale"]
    dof_vel_scale = config["dof_vel_scale"]
    action_scale = config["action_scale"]
    cmd_scale = np.array(config["cmd_scale"], dtype=np.float32)
    num_actions = config["num_actions"]
    num_obs = config["num_obs"]
    cmd = np.array([args.cmd_x, 0.0, 0.0], dtype=np.float32)

    print(f"[INFO] Loading policy: {policy_path}")
    print(f"[INFO] Loading robot xml: {xml_path}")
    print(f"[INFO] Command (vx, vy, wz): {cmd}")

    # ---------- Init state ----------
    action = np.zeros(num_actions, dtype=np.float32)
    target_dof_pos = default_angles.copy()
    obs_buf = np.zeros(num_obs, dtype=np.float32)
    counter = 0

    # ---------- Load MuJoCo model ----------
    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)
    m.opt.timestep = simulation_dt

    # ---------- Load policy ----------
    policy = torch.jit.load(policy_path)
    policy.eval()

    # ---------- Renderer ----------
    renderer = mujoco.Renderer(m, height=args.height, width=args.width)

    # Camera that follows the robot from a side-rear angle
    cam = mujoco.MjvCamera()
    mujoco.mjv_defaultCamera(cam)
    cam.distance = 3.5
    cam.elevation = -15
    cam.azimuth = 135  # side-rear view
    cam.lookat[:] = np.array([0.0, 0.0, 0.7])

    # ---------- Video writer ----------
    output_path = os.path.join(LEGGED_GYM_ROOT_DIR, "logs", args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    writer = imageio.get_writer(output_path, fps=args.fps,
                                codec="libx264", quality=8)

    # ---------- Simulation loop ----------
    total_steps = int(args.duration / simulation_dt)
    frames_per_render = int(1.0 / args.fps / simulation_dt)  # how many sim steps per video frame

    print(f"[INFO] Will run {total_steps} sim steps "
          f"({args.duration}s real time), capturing every {frames_per_render} steps "
          f"-> ~{total_steps // frames_per_render} frames @ {args.fps}fps")

    for step in range(total_steps):
        # PD torque
        tau = pd_control(target_dof_pos, d.qpos[7:], kps,
                         np.zeros_like(kds), d.qvel[6:], kds)
        d.ctrl[:] = tau
        mujoco.mj_step(m, d)

        counter += 1
        if counter % control_decimation == 0:
            # Build observation
            qj = d.qpos[7:]
            dqj = d.qvel[6:]
            quat = d.qpos[3:7]
            omega = d.qvel[3:6]

            qj_scaled = (qj - default_angles) * dof_pos_scale
            dqj_scaled = dqj * dof_vel_scale
            gravity = get_gravity_orientation(quat)
            omega_scaled = omega * ang_vel_scale

            period = 0.8
            t = counter * simulation_dt
            phase = (t % period) / period
            sin_phase = np.sin(2 * np.pi * phase)
            cos_phase = np.cos(2 * np.pi * phase)

            obs_buf[:3] = omega_scaled
            obs_buf[3:6] = gravity
            obs_buf[6:9] = cmd * cmd_scale
            obs_buf[9:9 + num_actions] = qj_scaled
            obs_buf[9 + num_actions:9 + 2 * num_actions] = dqj_scaled
            obs_buf[9 + 2 * num_actions:9 + 3 * num_actions] = action
            obs_buf[9 + 3 * num_actions:9 + 3 * num_actions + 2] = \
                np.array([sin_phase, cos_phase])

            with torch.no_grad():
                obs_tensor = torch.from_numpy(obs_buf).unsqueeze(0)
                action_tensor = policy(obs_tensor)
                action = action_tensor.detach().numpy().squeeze()

            target_dof_pos = action * action_scale + default_angles

        # Render frame
        if step % frames_per_render == 0:
            # Camera follows the robot's base position (qpos[0:3])
            cam.lookat[0] = d.qpos[0]
            cam.lookat[1] = d.qpos[1]
            cam.lookat[2] = d.qpos[2] + 0.3

            renderer.update_scene(d, camera=cam)
            frame = renderer.render()
            writer.append_data(frame)

            if (step // frames_per_render) % 30 == 0:
                print(f"  step {step}/{total_steps}, "
                      f"robot pos = ({d.qpos[0]:.2f}, {d.qpos[1]:.2f}, {d.qpos[2]:.2f})")

    writer.close()
    print(f"\n[DONE] Video saved to: {output_path}")
    print(f"[INFO] Final robot position: x={d.qpos[0]:.3f}, y={d.qpos[1]:.3f}, z={d.qpos[2]:.3f}")
    if d.qpos[2] < 0.3:
        print("[WARN] Robot height < 0.3m, likely fell over.")
    else:
        print("[OK] Robot stayed upright.")
