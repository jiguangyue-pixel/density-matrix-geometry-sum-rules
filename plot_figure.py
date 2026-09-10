"""Submitted Figure 1 plotting routine with portable data/output paths."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.ticker import NullFormatter
from figure_style import STYLE, style

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "output/pdf"
TSTAR, H = 1., .005
NAME = "fig1_thermal_critical_response"
ORDER = [("M", 1), ("I", 0), ("U", 2)]
COLORS = {"M": "#0072B2", "I": "#D55E00", "U": "#CC79A7"}

def main_figure():
    local = np.load(DATA / "plot_data.npz")
    thermal = np.load(DATA / "thermal_extended.npz")
    ref = float(local["reference"])
    np.testing.assert_equal(ref, thermal["reference"])
    style()
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial"],
                         "font.size": 8, "legend.fontsize": 8, "axes.labelsize": 8,
                         "xtick.labelsize": 8, "ytick.labelsize": 8,
                         "axes.linewidth": 1, "xtick.major.width": 1,
                         "ytick.major.width": 1, "xtick.minor.width": 1,
                         "ytick.minor.width": 1})
    fig, axes = plt.subplots(1, 3, figsize=(180/25.4, 58/25.4),
                             gridspec_kw={"width_ratios": [1, 1, 1.08]})
    fig.subplots_adjust(left=.073, right=.985, bottom=.205, top=.91, wspace=.43)
    plotted = []

    def line(ax, x, y, key):
        label = STYLE[key][2]
        artist, = ax.plot(x, y, color=COLORS[key], ls="-", lw=1.5, label=label)
        artist.set_gid(key)
        np.testing.assert_array_equal(artist.get_ydata(), y)
        plotted.append(artist)
        return artist

    ax = axes[0]
    tt = thermal["T"]
    selected = local["selected_T_values"]
    x = np.r_[tt, TSTAR]
    sort = np.argsort(x)
    handles = []
    for key, col in ORDER:
        y = np.r_[thermal["moments"][:, col], selected[col]] / ref
        handles.append(line(ax, x[sort], y[sort], key))
    ax.set_xscale("log")
    ax.set_xlim(.01, 10)
    ax.set_xticks([.01, .1, 1, 10],
                 [r"$10^{-2}$", r"$10^{-1}$", r"$10^0$", r"$10^1$"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_ylim(0, 1.08)
    ax.set_yticks([0, .25, .5, .75, 1])
    ax.axhline(.5, color=".7", lw=1, ls=(0, (3, 3)), zorder=0)
    ax.set_xlabel(r"$k_{\rm B}T/t_1$")
    ax.set_ylabel(r"$\widetilde{\mathcal{W}}_X^{xy}/\mathcal{M}_{\rm ref}$")
    ax.text(.96, .94, r"$g=0.8$", transform=ax.transAxes,
            fontsize=8, ha="right", va="top")
    common = ax.legend(handles=handles, loc="lower left", frameon=False,
                       handlelength=2.5, handletextpad=.6,
                       labelspacing=.4, borderaxespad=.6)

    ax = axes[1]
    for key, col in ORDER:
        line(ax, local["phase_g"], local["phase_moments"][:, col]/ref, key)
    ax.set_xlim(.5, 1.5)
    ax.set_ylim(0, 1.4)
    ax.set_xticks([.5, .75, 1, 1.25, 1.5])
    ax.set_yticks([0, .4, .8, 1.2])
    ax.set_ylabel(r"$\widetilde{\mathcal{W}}_X^{xy}/\mathcal{M}_{\rm ref}$")
    ax.text(.96, .72, rf"$k_{{\rm B}}T/t_1={TSTAR:g}$", transform=ax.transAxes,
            ha="right", fontsize=8)
    for pos, text in [(.20, r"$C=1$"), (.80, r"$C=0$")]:
        ax.text(pos, .975, text, transform=ax.transAxes, fontsize=8,
                ha="center", va="top", color=".30")

    ax = axes[2]
    for key, col in ORDER:
        line(ax, local["g"], local["slopes"][:, col], key)
    ax.set_xlim(.9, 1.1)
    ax.set_xticks([.9, .95, 1, 1.05, 1.1])
    ax.set_ylim(.2, 3.05)
    ax.set_yticks([.5, 1, 1.5, 2, 2.5, 3])
    ax.set_ylabel(r"$-\partial_g(\widetilde{\mathcal{W}}_X^{xy}/\mathcal{M}_{\rm ref})$")
    ax.text(.96, .965, rf"$k_{{\rm B}}T/t_1={TSTAR:g}$", transform=ax.transAxes,
            ha="right", va="top", fontsize=8)
    for ax in axes[1:]:
        ax.axvline(1, color=".7", lw=1, ls=(0, (1, 3)), zorder=0)
        ax.set_xlabel(r"$g=\Delta/\Delta_c$")
    for ax, letter in zip(axes, "abc"):
        ax.tick_params(direction="in", top=True, right=True, width=1, length=3, pad=3)
        ax.text(-.035, 1.03, letter, transform=ax.transAxes,
                fontweight="bold", fontsize=8, va="bottom", ha="right")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    overflow = []
    for artist in fig.findobj(Text):
        if artist.get_visible() and artist.get_text():
            box = artist.get_window_extent(renderer)
            if box.width and box.height and not (
                    box.x0 >= -1 and box.y0 >= -1
                    and box.x1 <= fig.bbox.width+1 and box.y1 <= fig.bbox.height+1):
                overflow.append(artist.get_text())
    assert not overflow, overflow
    assert len(plotted) == 9
    for artist in plotted:
        key = artist.get_gid()
        assert artist.get_color() == COLORS[key]
        assert artist.get_linestyle() == "-"
    assert [t.get_text() for t in common.get_texts()] == [STYLE[k][2] for k, _ in ORDER]
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / (NAME+".pdf"))
    fig.savefig(OUT / (NAME+".png"), dpi=300)
    with (OUT.parent / "Fig1_source_data.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["panel", "quantity", "x", "normalized_y",
                         "x_variable", "kBT_over_t1", "g_fixed",
                         "central_difference_half_step", "M_reference"])
        for index, artist in enumerate(plotted):
            part = index // 3
            for xvalue, yvalue in zip(artist.get_xdata(), artist.get_ydata()):
                writer.writerow(["abc"[part], artist.get_gid(), xvalue, yvalue,
                                 "kBT/t1" if part == 0 else "g=Delta/Delta_c",
                                 xvalue if part == 0 else TSTAR,
                                 .8 if part == 0 else "",
                                 H if part == 2 else "", ref])
    plt.close(fig)
    return {"data_curves_verified": 9, "consistent_styles": True,
            "text_outside_canvas": overflow, "shared_legend": True,
            "legend_panel": "a", "figure_size_mm": [180, 58], "data_lines_solid": True,
            "non_math_font": "Arial", "minimum_stroke_pt": 1}
