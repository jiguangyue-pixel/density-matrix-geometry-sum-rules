"""Plot labels and style used for the submitted figure."""
import matplotlib.pyplot as plt

STYLE = {
    "M": ("#006494", "-", r"$\widetilde{\mathcal{M}}^{xy}$"),
    "I": ("#C43C39", "--", r"$\widetilde{I}^{xy}$"),
    "U": ("#16877C", "-.", r"$\widetilde{U}_{(1)}^{xy}$"),
    "D": ("#75459A", ":", r"$\widetilde{\mathcal{M}}^{xy}-\widetilde{I}^{xy}$"),
}

def style():
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "STIXGeneral"],
        "mathtext.fontset": "stix", "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5,
        "axes.linewidth": .65, "lines.linewidth": 1.35, "pdf.fonttype": 42,
        "axes.unicode_minus": False})
