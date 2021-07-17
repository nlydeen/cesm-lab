#!/usr/bin/env python

import numpy as np

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

from common import REF_VALUES, get_run_specs_info, read_run_specs


if __name__ == "__main__":
    n_iter, _ = get_run_specs_info()
    n_iter += 1

    hist = []

    for i in range(n_iter):
        hist.append(read_run_specs(i).theta)

    param_names = hist[-1].columns

    hist = np.array([x.values for x in hist])

    fig, axes = plt.subplots(hist.shape[2], sharex=True)

    for i, ax in enumerate(axes):
        ax.plot(hist[:, :, i].mean(axis=1), color="blue", label="Mean")

        low, high = np.percentile(hist[:, :, i], [25, 75], axis=1)
        ax.fill_between(np.arange(n_iter), low, high, color="blue", alpha=0.25,
                        label="25th/75th %iles")

        ax.axhline(REF_VALUES[i], color="red", linestyle="--")

        ax.set_title(param_names[i])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        if i == 0:
            ax.legend()

    plt.tight_layout()
    plt.savefig("history.png")
