import os
import pathlib
import shutil
from typing import Optional, Callable

import imageio
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from job_shop_lib import JobShopInstance, Dispatcher, Schedule
from job_shop_lib.solvers import DispatchingRuleSolver
from job_shop_lib.visualization.gantt_chart import plot_gantt_chart


# pylint: disable=too-many-arguments
def create_gif(
    gif_path: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    plot_function: Optional[Callable[[Schedule, int], Figure]] = None,
    fps: int = 1,
    remove_frames: bool = True,
    frames_dir: str | None = None,
    plot_current_time: bool = True,
) -> None:
    """Creates a GIF of the schedule being built by the given solver.

    Args:
        gif_path:
            The path to save the GIF file. It should end with ".gif".
        instance:
            The instance of the job shop problem to be scheduled.
        solver:
            The dispatching rule solver to use.
        plot_function:
            A function that plots a Gantt chart for a schedule. It
            should take a `Schedule` object and the makespan of the schedule as
            input and return a `Figure` object. If not provided, a default
            function is used.
        fps:
            The number of frames per second in the GIF.
        remove_frames:
            Whether to remove the frames after creating the GIF.
        frames_dir:
            The directory to save the frames in. If not provided,
            `gif_path.replace(".gif", "") + "_frames"` is used.
        plot_current_time:
            Whether to plot a vertical line at the current time.
    """
    if plot_function is None:
        plot_function = get_plot_function()

    if frames_dir is None:
        # Use the name of the GIF file as the directory name
        frames_dir = gif_path.replace(".gif", "") + "_frames"
    path = pathlib.Path(frames_dir)
    path.mkdir(exist_ok=True)
    frames_dir = str(path)
    create_gantt_chart_frames(
        frames_dir, instance, solver, plot_function, plot_current_time
    )
    create_gif_from_frames(frames_dir, gif_path, fps)

    if remove_frames:
        shutil.rmtree(frames_dir)


def get_plot_function(
    title: Optional[str] = None, cmap: str = "viridis"
) -> Callable[[Schedule, int], Figure]:
    """Returns a function that plots a Gantt chart for an unfinished schedule.

    Args:
        title: The title of the Gantt chart.
        cmap: The name of the colormap to use.

    Returns:
        A function that plots a Gantt chart for a schedule. The function takes
        a `Schedule` object and the makespan of the schedule as input and
        returns a `Figure` object.
    """

    def plot_function(schedule: Schedule, makespan: int) -> Figure:
        fig, _ = plot_gantt_chart(
            schedule, title=title, cmap_name=cmap, xlim=makespan
        )
        return fig

    return plot_function


def create_gantt_chart_frames(
    frames_dir: str,
    instance: JobShopInstance,
    solver: DispatchingRuleSolver,
    plot_function: Callable[[Schedule, int], Figure],
    plot_current_time: bool = True,
) -> None:
    """Creates frames of the Gantt chart for the schedule being built.
    
    Args:
        frames_dir:
            The directory to save the frames in.
        instance:
            The instance of the job shop problem to be scheduled.
        solver:
            The dispatching rule solver to use.
        plot_function:
            A function that plots a Gantt chart for a schedule. It
            should take a `Schedule` object and the makespan of the schedule as
            input and return a `Figure` object.
        plot_current_time:
            Whether to plot a vertical line at the current time."""
    dispatcher = Dispatcher(instance)
    schedule = dispatcher.schedule
    makespan = solver(instance).makespan()
    iteration = 0

    while not schedule.is_complete():
        solver.step(dispatcher)
        iteration += 1
        fig = plot_function(schedule, makespan)
        current_time = (
            None if not plot_current_time else dispatcher.current_time()
        )
        _save_frame(fig, frames_dir, iteration, current_time)


def _save_frame(
    figure: Figure, frames_dir: str, number: int, current_time: int | None
) -> None:
    if current_time is not None:
        figure.gca().axvline(current_time, color="red", linestyle="--")

    figure.savefig(f"{frames_dir}/frame_{number:02d}.png", bbox_inches="tight")
    plt.close(figure)


def create_gif_from_frames(frames_dir: str, gif_path: str, fps: int) -> None:
    """Creates a GIF from the frames in the given directory.
    
    Args:
        frames_dir:
            The directory containing the frames to be used in the GIF.
        gif_path:
            The path to save the GIF file. It should end with ".gif".
        fps:
            The number of frames per second in the GIF.
    """
    frames = [
        os.path.join(frames_dir, frame)
        for frame in sorted(os.listdir(frames_dir))
    ]
    images = [imageio.imread(frame) for frame in frames]
    imageio.mimsave(gif_path, images, fps=fps, loop=0)
