#!/usr/bin/env python

import numpy as np

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.stats import t

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

        t_c = t.ppf(0.975, hist.shape[1] - 1)
        half_ci = t_c * hist[:, :, i].std(ddof=1, axis=1) / np.sqrt(n_params)

        ax.plot(means, color="#5e81ac", label="Mean")
        ax.fill_between(np.arange(n_iter), means - half_ci, means + half_ci,
                        color="#5e81ac", alpha=0.25, label="95% CI")

        ax.axhline(REF_VALUES[i], color="#bf616a", linestyle="--",
                   label="Reference")

        ax.set_title(param_names[i])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        ax.set_xlim(0, n_iter - 1)
        ax.grid(color="k", alpha=0.05)

        if i == 0:
            ax.legend()

    plt.tight_layout()
    plt.savefig("history.png", dpi=300)
