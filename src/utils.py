import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from .environment import Easy21
from .agent import RLearningAgent


def _generate_filepath(output_dir: str, agent: RLearningAgent):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return os.path.join(output_dir, agent.base_name)


def train_and_plot(
    steps: int, agent: RLearningAgent, env: Easy21, output_dir: str, frames=50
):
    """
    Plots a value function as a surface plot, like in: https://goo.gl/aF2doj

    You can choose between just plotting the graph for the value function
    which is the default behaviour (generate_gif=False) or to train the agent
    a couple of times and save the frames in a gif as you train.

    args:
        agent.
        title (string): plot title.
        generate_gif (boolean): if want to save plots as a gif.
        train_steps: if is not None and generate_gif = True, then will use this
                    value as the number of steps to train the model at each frame.
    """
    filepath = _generate_filepath(output_dir, agent)

    # you can change this values to change the size of the graph
    fig = plt.figure("Value function", figsize=(10, 5))

    # Explanation about this line: https://goo.gl/LH5E7i
    ax = fig.add_subplot(111, projection="3d")

    def plot_frame(ax):

        V = agent.get_action_values()

        # min value allowed accordingly with the documentation is 1
        # we're getting the max value from V dimensions
        min_x = 1
        max_x = V.shape[0]
        min_y = 1
        max_y = V.shape[1]

        # creates a sequence from min to max
        x_range = np.arange(min_x, max_x)
        y_range = np.arange(min_y, max_y)

        # creates a grid representation of x_range and y_range
        X, Y = np.meshgrid(x_range, y_range)

        # get value function for X and Y values
        def get_stat_val(x, y):
            return V[x, y].max(axis=-1)

        Z = get_stat_val(X, Y)

        # creates a surface to be ploted
        # check documentation for details: https://goo.gl/etEhPP
        ax.set_xlabel("Dealer Showing")
        ax.set_ylabel("Player Sum")
        ax.set_zlabel("Value")

        return ax.plot_surface(
            X,
            Y,
            Z,
            rstride=1,
            cstride=1,
            cmap=cm.coolwarm,
            linewidth=0,
            antialiased=False,
        )

    steps = steps // frames

    def animate(frame):
        i = steps * frame
        agent.train(steps, env)

        # clear the plot and create a new surface
        ax.clear()
        surf = plot_frame(ax)
        plt.title("Iteration %s" % i)
        fig.canvas.draw()
        return surf

    ani = animation.FuncAnimation(fig, animate, frames, repeat=False)
    ani.save(filepath + ".gif", writer="imagemagick", fps=3)


def plot_error_vs_episode(
    sqrt_error,
    lambdas,
    train_steps=1000000,
    eval_steps=1000,
    title="SQRT error VS episode number",
    save_as_file=False,
):
    """
        Given the sqrt error between sarsa(lambda) for multiple lambdas and
        an already trained MC control model this function plots a
        graph: sqrt error VS episode number.

        Args:
            sqrt_error (tensor): multiD tensor.
            lambdas (tensor): 1D tensor.
            train_steps (int): number the total steps used to train the models.
            eval_steps (int): train_steps/eval_steps is the number of time the
                              errors were calculated while training.
            save_as_file (boolean).
    """
    # avoid zero division
    assert eval_steps != 0
    x_range = np.arange(0, train_steps, eval_steps)

    # assert that the inputs are correct
    assert len(sqrt_error) == len(lambdas)
    for e in sqrt_error:
        assert len(list(x_range)) == len(e)

    # create plot
    fig = plt.figure(title, figsize=(12, 6))
    plt.title(title)
    ax = fig.add_subplot(111)

    for i in xrange(len(sqrt_error) - 1, -1, -1):
        ax.plot(x_range, sqrt_error[i], label="lambda %.2f" % lambdas[i])

    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    if save_as_file:
        plt.savefig(title)
    plt.show()


def plot_error_vs_lambda(
    sqrt_error, lambdas, title="SQRT error vs lambda", save_as_file=False
):
    """
        Given the sqrt error between sarsa(lambda) for multiple lambdas and
        an already trainedMC Control ths function plots a graph:
        sqrt error VS lambda.

        Args:
            sqrt_error (tensor): multiD tensor.
            lambdas (tensor): 1D tensor.
            title (string): Plot title.
            save_as_file (boolean).

        The srt_error 1D length must be equal to the lambdas length.
    """

    # assert input is correct
    assert len(sqrt_error) == len(lambdas)

    # create plot
    fig = plt.figure(title, figsize=(12, 6))
    plt.title(title)
    ax = fig.add_subplot(111)

    # Y are the last values found at sqrt_error
    y = [s[-1] for s in sqrt_error]
    ax.plot(lambdas, y)

    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
    if save_as_file:
        plt.savefig(title)
    plt.show()