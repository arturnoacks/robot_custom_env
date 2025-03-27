import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
import os
import robot_env    # Even though we don't use this class here, we should include it here so that it registers the WarehouseRobot environment.

# Train or test using Q-Learning
def run_q(episodes, is_training=True, render=None):

    env = gym.make('robot-v0', render_mode='human' if render else None)

    if(is_training):
        # If training, initialize the Q Table, a 5D vector: [robot_row_pos, robot_row_col, target_row_pos, target_col_pos, actions]
        q = np.zeros((env.unwrapped.grid_cols, env.unwrapped.grid_cols, env.unwrapped.grid_cols, env.action_space.n))
    else:
        # If testing, load Q Table from file.
        f = open('q_table.pkl', 'rb')
        q = pickle.load(f)
        f.close()

    # Hyperparameters
    learning_rate_a = 0.9   # alpha or learning rate
    discount_factor_g = 0.9 # gamma or discount rate. Near 0: more weight/reward placed on immediate state. Near 1: more on future state.
    epsilon = 1             # 1 = 100% random actions

    # Array to keep track of the number of steps per episode for the robot to find the target.
    # We know that the robot will inevitably find the target, so the reward is always obtained,
    # so we want to know if the robot is reaching the target efficiently.
    steps_per_episode = np.zeros(episodes)
    reward_per_episode = np.zeros(episodes)

    step_count = 0
    reward_count = 0
    for i in range(episodes):
        if(render):
            print(f'Episode {i}')

        # Reset environment at teh beginning of episode
        state = env.reset()[0]
        terminated = False

        # Robot keeps going until it finds the target
        while(not terminated):

            # Select action based on epsilon-greedy
            if is_training and random.random() < epsilon:
                # select random action
                action = env.action_space.sample()
            else:                
                # Convert state of [1,2,3,4] to (1,2,3,4), use this to index into the 4th dimension of the 5D array.
                q_state_idx = tuple(state) 

                # select best action
                action = np.argmax(q[q_state_idx])
            
            # Perform action
            new_state,reward,terminated,_,_ = env.step(action)

            # Convert state of [1,2,3,4] and action of [1] into (1,2,3,4,1), use this to index into the 5th dimension of the 5D array.
            q_state_action_idx = tuple(state) + (action,)

            # Convert new_state of [1,2,3,4] into (1,2,3,4), use this to index into the 4th dimension of the 5D array.
            q_new_state_idx = tuple(new_state)

            if is_training:
                # Update Q-Table
                q[q_state_action_idx] = q[q_state_action_idx] + learning_rate_a * (
                        reward + discount_factor_g * np.max(q[q_new_state_idx]) - q[q_state_action_idx]
                )

            # Update current state
            state = new_state

            # Record steps
            step_count+=1
            reward_count += reward
            if terminated:
                steps_per_episode[i] = step_count
                reward_per_episode[i] = reward_count + 100 # +100 offset
                step_count = 0
                reward_count = 0

        # Decrease epsilon
        epsilon = max(epsilon - 1/episodes, 0)

    env.close()

    # Graph steps
    sum_steps = np.zeros(episodes)
    sum_rewards = np.zeros(episodes)
    for t in range(episodes):
        sum_steps[t] = np.mean(steps_per_episode[max(0, t-100):(t+1)]) # Average steps per 100 episodes
        sum_rewards[t] = np.mean(reward_per_episode[max(0, t-100):(t+1)])
    

    plt.xlabel("Episode no.")
    plt.plot(sum_steps, label = "Steps per episode")
    plt.plot(sum_rewards, label = "Score per episode")
    plt.legend(loc = "upper left")
    plt.savefig('solution.png')

    if is_training:
        f = open("q_table.pkl","wb")
        pickle.dump(q, f)
        f.close()


if __name__ == '__main__':

    # Train/test using Q-Learning
    run_q(5000, is_training=True, render=False)