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
    n_params = len(param_names)

    hist = np.array([x.values for x in hist])

    fig, axes = plt.subplots(n_params, sharex=True)

    for i, ax in enumerate(axes):
        means = hist[:, :, i].mean(axis=1)
        half_ci = 1.96 * hist[:, :, i].std(axis=1) / np.sqrt(n_params)

        ax.plot(means, color="blue", label="Mean")
        ax.fill_between(np.arange(n_iter), means - half_ci, means + half_ci,
                        color="blue", alpha=0.25, label="95% CI")

        ax.axhline(REF_VALUES[i], color="red", linestyle="--")

        ax.set_title(param_names[i])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        if i == 0:
            ax.legend()

    plt.tight_layout()
    plt.savefig("history.png")
