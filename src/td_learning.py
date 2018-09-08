import os
import gc
import pickle
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from mpl_toolkits.mplot3d import Axes3D
from src.agent import RLearningAgent


class TDLearningAgent(RLearningAgent):

    def __init__(self, possible_actions, n_0=100, gamma=1,
                 base_name='td_learning'):
        self._possible_actions = possible_actions
        self._n_actions = len(possible_actions)
        self._gamma = gamma
        self._n_0 = n_0
        self._base_name = base_name
        self._action2id = dict(zip(possible_actions, range(self._n_actions)))
        self._id2action = dict(zip(range(self._n_actions), possible_actions))
        self._state_action_values = np.zeros(
            (11, 22, self._n_actions), dtype=np.float32)
        self._state_action_visits = np.zeros(
            (11, 22, self._n_actions), dtype=np.float32)
        self._past_actions = deque([], 2)
        self._past_states = deque([], 2)
        self._past_returns = deque([], 2)

    def take_action(self, state, explore=True):

        n_0 = self._n_0

        epsilon = n_0 / (n_0 + self._state_action_visits.take(state).sum())

        # Choose action based on Epsilon-Greedy
        if explore and random.random() < epsilon:
            action_id = random.choice(range(self._n_actions))
        else:
            action_values = self._state_action_values.take(state)
            action_id = np.argmax(action_values)

        return self._possible_actions[action_id]

    def observe_and_act(self, state, reward=None, terminate=False):

        action = None

        if not terminate:
            action = self.take_action(state)
            self._memorize(state, action)

        if reward is not None:
            self._past_returns.append(reward)
            self._update(terminate)

        if terminate:
            self._clear_cache()

        return action

    def _memorize(self, state, action):
        action_id = self._action2id[action]
        self._past_states.append(state)
        self._past_actions.append(action_id)

    def _update(self, terminate):

        gamma = self._gamma
        past_states = self._past_states
        past_actions = self._past_actions
        past_returns = self._past_returns

        if terminate and len(past_states) == 1:
            d_H_1, p_H_1 = past_states[0]
            a_1 = past_actions[0]
        else:
            (d_H, p_H), (d_H_1, p_H_1) = past_states[0], past_states[1]
            a, a_1 = past_actions

        r = past_returns.popleft()

        # Increase Q(s, a)
        if not terminate:
            self._state_action_visits[d_H, p_H, a] += 1
            # q(s, a) += 1 / n(s, a) * (r + gammba * q(s', a') - q(s, a))
            self._state_action_values[d_H, p_H, a] += \
                ((r + gamma * self._state_action_values[d_H_1, p_H_1, a_1] -
                  self._state_action_values[d_H, p_H, a]) /
                    self._state_action_visits[d_H, p_H, a])
        else:
            self._state_action_visits[d_H_1, p_H_1, a_1] += 1
            # q(s, a) += 1 / n(s, a) * (r - q(s, a))
            self._state_action_values[d_H_1, p_H_1, a_1] += \
                ((r - self._state_action_values[d_H_1, p_H_1, a_1]) /
                    self._state_action_visits[d_H_1, p_H_1, a_1])

    def _clear_cache(self):
        self._past_actions = deque([], 2)
        self._past_states = deque([], 2)
        self._past_returns = deque([], 2)
        gc.collect()

    def save(self, output_dir, iteration=None):

        output_dir = os.path.join(output_dir, self._base_name)

        # Clear cache to avoid saving unnecessary data
        self._clear_cache()

        # Convert numpy array to list for pickability
        self._state_action_values = self._state_action_values.tolist()
        self._state_action_visits = self._state_action_visits.tolist()

        # Pickle class
        self._save_local(output_dir, iteration, extension='pkl')

        # Convert back to numpy array for reusability
        self._state_action_values = np.asarray(self._state_action_values)
        self._state_action_visits = np.asarray(self._state_action_visits)

        # Save plots
        self._save_plot(output_dir, iteration)

    def _save_plot(self, output_dir, iteration=None):

        x, y = np.meshgrid(np.arange(1, 11),
                           np.arange(1, 22))

        state_action_values = self._state_action_values[1:, 1:, 0].T
        state_action_visits = self._state_action_visits[1:, 1:, 0].T

        fig = plt.figure()

        ax = fig.add_subplot(1, 2, 1, projection='3d')
        ax.plot_surface(x, y, state_action_values,
                        cmap='viridis', edgecolor='none')
        ax.set_title('State action values')

        ax = fig.add_subplot(1, 2, 2, projection='3d')
        ax.plot_surface(x, y, state_action_visits,
                        cmap='viridis', edgecolor='none')
        ax.set_title('State action visits')

        self._save_local(output_dir, iteration, extension='png')

    def load(fname):
        with open(fname, 'rb') as f:
            self = pickle.load(f)
        self._state_action_values = np.asarray(self._state_action_values)
        self._state_action_visits = np.asarray(self._state_action_visits)
        return self
