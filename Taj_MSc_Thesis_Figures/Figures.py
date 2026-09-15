import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import interp1d
from brukeropus import read_opus
import numpy as np
import shutil
import os
import stat

mpl.rcParams.update({
    "font.family": "STIXGeneral",
    "mathtext.fontset": "stix",

    # Font sizes
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,

    # Default grid
    "axes.grid": True,
    "grid.alpha": 0.3
})


def force_remove(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def minmax(arr):
    return (arr - arr.min()) / (arr.max() - arr.min())


def Norm(ATR, min_value=0, max_value=1):
    ATR.iloc[:, 1] = pd.to_numeric(ATR.iloc[:, 1], errors='coerce')
    min_val = ATR.iloc[:, 1].min()
    max_val = ATR.iloc[:, 1].max()
    ATR['norm'] = ((ATR.iloc[:, 1] - min_val) / (max_val - min_val)) \
        * (max_value - min_value) + min_value


def coloring(keys):
    return ['#8B0000', '#FF8C00', '#D2B48C', '#A0522D', '#708090', '#2E8B57']


def saveFig(name="Fig", folder="", fig=None, dataType=[]):
    path = folder + "\\" + name + ".pdf"
    fig.savefig(path, format="pdf", bbox_inches="tight")
    print(f"Saved: {name} -----> {path}")
    return


def makePlot(Files, Titles=["Placeholder Title"], Legend=None,
             offset=None, xlim=None, ylim=None, dataType=[], splot=1,
             TOver=None, mmNorm=False, highlight=None):
    color = ["Blue", "Orange", "Green", "Purple"]
    if splot == 1:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title(Titles[0])
        ax.set_xlabel(r'Wavenumber (cm$^{-1}$)')
        ax.set_ylabel("Absorbance")
        ax.invert_xaxis()

        if highlight is not None and isinstance(highlight, list):
            ax.axvspan(highlight[0], highlight[1], color="red", alpha=0.2)
        if xlim is not None:
            ax.set_xlim(xlim if not isinstance(xlim, list) else xlim[0])
        if ylim is not None:
            ax.set_ylim(ylim if not isinstance(ylim, list) else ylim[0])

        for i, file in enumerate(Files):
            f = read_opus(file)
            x = getattr(f, dataType[i]).x
            y = getattr(f, dataType[i]).y

            if TOver is not None and isinstance(TOver, list):
                if TOver[i] != 0:
                    mask = x >= TOver[i]
                    x = x[mask]
                    y = y[mask]

            if mmNorm:
                y = minmax(y)

            if offset is not None:
                ax.plot(x, y + offset[i], color=color[i],
                        label=Legend[i] if Legend is not None else None)
                ax.set_ylabel("")
                ax.set_yticks([])
            else:
                ax.plot(x, y, color=color[i],
                        label=Legend[i] if Legend is not None else None)

            if Legend is not None:
                ax.legend()

    else:
        fig, axes = plt.subplots(splot, 1, figsize=(15, 10), sharex=True)

        for i in range(splot):
            ax = axes[i]
            f = read_opus(Files[i])
            data = getattr(f, dataType[i])
            x = data.x
            y = data.y

            if TOver is not None and isinstance(TOver, list):
                if TOver[i] != 0:
                    mask = x >= TOver[i]
                    x = x[mask]
                    y = y[mask]

            if mmNorm:
                y = minmax(y)

            ax.plot(x, y, color=color[i],
                    label=Legend[i] if Legend is not None else None)
            ax.set_ylabel("Absorbance")

            ax.set_title(Titles[i])

            if xlim is not None:
                if isinstance(xlim, list):
                    ax.set_xlim(xlim[i])

                else:
                    ax.set_xlim(xlim)

            # Apply per‑subplot ylim
            if ylim is not None:
                if isinstance(ylim, list):
                    ax.set_ylim(ylim[i])
                else:
                    ax.set_ylim(ylim)

            if Legend is not None:
                ax.legend()

        ax.invert_xaxis()
        axes[-1].set_xlabel(r'Wavenumber (cm$^{-1}$)')

    return fig


path = r"Figures"

if os.path.exists(path):
    shutil.rmtree(path, onerror=force_remove)

else:
    pass

if not os.path.exists(path):
    os.makedirs(path)

    for i in range(1, 4):
        os.makedirs(os.path.join(path, f"Chapter_{i}"))


else:
    print("Error: Figures folder already exists and cannot be removed.")

Chapters = [r'Figures\Chapter_1', r'Figures\Chapter_2', r'Figures\Chapter_3',
            r'Figures\Chapter_4', r'Figures\Appendix']

# Chapter 1
Files = [r"IR-Spectra\BEA0001_CO_ATR_20251216_01.0"]

f = read_opus(Files[0])

x = f.a.x
y = f.a.y

fig, (ax_top, ax_bot) = plt.subplots(
    2, 1, sharex=True, figsize=(10, 6),
    gridspec_kw={'height_ratios': [8, 1]}
)
fig.subplots_adjust(hspace=0.05)
fig.gca().invert_xaxis()
# ============================================================
# TOP AXIS (VISIBLE REGION)
# ============================================================
ax_top.plot(x, y, color="blue")
ax_top.invert_xaxis()
ax_top.set_ylim(0.07, 0.165)
ax_top.set_title("Raw Biochar Spectrum")

# ============================================================
# OFFSET LINE USING FIGURE COORDINATES WITH <-> ARROW
# ============================================================

offset_y = 0.075  # horizontal dashed line on top axis
ax_top.axhline(offset_y, color="black", linestyle="--", linewidth=1.5)

# X-position for the arrow (LEFT side near 4000 cm⁻¹)
x_pos = max(x) - 0.95*(max(x) - min(x))   # move arrow far left

# --- Convert bottom (0) and top (offset_y) to figure coordinates ---
x_fig_bottom, y_fig_bottom = ax_bot.transData.transform((x_pos, 0))
x_fig_top, y_fig_top = ax_top.transData.transform((x_pos, offset_y))

# Convert pixel coords → figure coords
x_fig_bottom, y_fig_bottom = fig.transFigure.inverted().transform(
    (x_fig_bottom, y_fig_bottom))
x_fig_top, y_fig_top = fig.transFigure.inverted().transform(
    (x_fig_top, y_fig_top))

# ============================================================
# DRAW ONE CONTINUOUS <-> ARROW ACROSS THE BREAK
# ============================================================
arrow = FancyArrowPatch(
    (x_fig_bottom, y_fig_bottom),
    (x_fig_top,    y_fig_top),
    transform=fig.transFigure,
    arrowstyle="<->",
    mutation_scale=20,
    linewidth=2,
    color="black"
)
fig.patches.append(arrow)

# ============================================================
# LABEL ON THE SAME (LEFT) SIDE
# ============================================================
label_x = x_fig_bottom   # nudge slightly left of arrow
label_y = (y_fig_bottom + y_fig_top) / 2

fig.text(
    label_x,
    label_y,
    "Offset",
    ha="center",
    va="center",
    fontsize=12,
    bbox=dict(facecolor="white", edgecolor="none", pad=0.2)
)

# --- SLOPE LINE (shifted upward) ---
x_start = 4000
x_end = 1750
y_start = 0.11
y_end = 0.075

ax_top.plot([x_start, x_end], [y_start, y_end],
            linestyle="--", color="black", linewidth=1.5)

mid_x = (x_start + x_end)/2
mid_y = (y_start + y_end)/2

ax_top.text(
    mid_x, mid_y,
    "Slope",
    ha="center",
    va="center",
    fontsize=12,
    bbox=dict(facecolor="white", edgecolor="none", pad=0.2)
)

# --- CURVATURE ARC (shifted upward) ---
# Adjustable parameters
x_center = 2650        # horizontal center of the arc
y_center = 0.035        # vertical center of the arc
width = 1600        # horizontal radius (controls how wide the curve is)
height = 0.065        # vertical radius (controls curvature strength)
theta1 = -300        # start angle (degrees)
theta2 = -240        # end angle (degrees)
right_drop = -0.03      # NEW PARAMETER: lowers the right side of the curve

theta = np.linspace(np.radians(theta1), np.radians(theta2), 200)
x_curve = x_center + width * np.cos(theta)
y_curve = y_center + height * np.sin(theta)

t = (x_curve - x_curve.min()) / (x_curve.max() - x_curve.min())
y_curve = y_curve - right_drop * t

ax_top.plot(x_curve, y_curve, linestyle="--", color="black", linewidth=1.5)

mid_idx = len(theta)//2
label_x = x_curve[mid_idx]
label_y = y_curve[mid_idx]

ax_top.text(
    label_x - 60,
    label_y,
    "Curvature",
    ha="center",
    va="center",
    fontsize=12,
    bbox=dict(facecolor="white", edgecolor="none", pad=0.0)
)

# ============================================================
# LABEL A PEAK AT A KNOWN WAVENUMBER
# ============================================================

peak_wn = 1585  # peak position
peak_y = np.interp(peak_wn, x, y)

# --- Vertical dashed line on TOP axis ---
ax_top.axvline(
    x=peak_wn,
    ymin=0, ymax=1,
    color="black",
    linestyle="--",
    linewidth=0.8   # thinner than horizontal dashed line
)

# --- Vertical dashed line on BOTTOM axis ---
ax_bot.axvline(
    x=peak_wn,
    ymin=0, ymax=1,
    color="black",
    linestyle="--",
    linewidth=0.8
)

# --- Label slightly above the peak on the TOP axis ---
ax_top.text(
    peak_wn,
    peak_y - 0.0175,
    "Peak",
    ha="center",
    va="bottom",
    fontsize=12,
    bbox=dict(facecolor="white", edgecolor="none", pad=0.2)
)


# ============================================================
# BOTTOM AXIS (ZERO REGION)
# ============================================================
ax_bot.plot(x, y, color="blue")
ax_bot.invert_xaxis()
ax_bot.set_ylim(0, 0.01)
ax_bot.set_xlabel(r"Wavenumber (cm$^{-1}$)")
# ============================================================
# ADD XTICKS TO THE BOTTOM AXIS
# ============================================================
xticks = np.arange(4000, 0, -500)   # 4000 → 3500 → … → 1000
ax_bot.set_xticks(xticks)
ax_bot.set_xticklabels([str(t) for t in xticks])


# ============================================================
# HIDE SPINES BETWEEN AXES
# ============================================================
ax_top.spines.bottom.set_visible(False)
ax_bot.spines.top.set_visible(False)

# Hide ticks on top axis only
ax_top.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

# Re-enable ticks on bottom axis
ax_bot.tick_params(axis="x", which="both", bottom=True, labelbottom=True)


# ============================================================
# SLANTED BREAK MARKERS
# ============================================================
d = 0.5
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)

ax_top.plot([0, 1], [0, 0], transform=ax_top.transAxes, **kwargs)
ax_bot.plot([0, 1], [1, 1], transform=ax_bot.transAxes, **kwargs)

# Add one overall y‑axis label for the entire figure
fig.text(
    0.065, 0.5,
    "Intensity",
    va="center",
    rotation="vertical",
    fontsize=14
)

saveFig(name="Figure 1.1", folder=Chapters[0], fig=fig)

# Chapter 2

Files = [r'IR-Spectra\BEA0002_ATR_20260318_01.0',
         r'IR-Spectra\BEA0002_ATR_20260318_01.0',
         r'IR-Spectra\BEA0002_ATR_20260318_01.0']
Files2 = [r"IR-Spectra\TEST_GE_BIOCHAR.0",
          r'IR-Spectra\BEA0002_ATR_20260318_01.0']
Files3 = [r"IR-Spectra\BlueCap-TEST36x36-Reflectance.0",
          r"IR-Spectra\BEA0001_CO2_01_ATRGE_20260130_01.0",
          r"IR-Spectra\BEA0002_ATR_20260318_02.0"]
Files4 = [r"IR-Spectra\TEST_GE_BIOCHAR.0",
          r"IR-Spectra\TEST_GE_BIOCHAR3.0",
          r"IR-Spectra\BEA0001_ATRGE_20260130_01.0"]
Files5 = [r"IR-Spectra\ACBC_IR_20241126_BEA001_2.0",
          r"IR-Spectra\ACBC_IR_20241126_BEA002_2.0",
          r"IR-Spectra\ACBC_IR_20241126_BEA003_2.0"]

fig = makePlot(Files,
               Titles=["Referene Spectra", "SSC Spectra",
                       "Absorbance Spectra"],
               dataType=["rf", "sm", "a"], splot=3)
fig2 = makePlot(Files2,
                Titles=["Biochar Spectra Taken With Germanium Crystal",
                        "Biochar Spectra Taken With Diamond Crystal"],
                dataType=["a", "a"], splot=2,
                ylim=[([-0.003, 0.006]), None], TOver=[600, 0])
fig3 = makePlot(Files3,
                Titles=["Spectrum of Air Taken Without a Crystal",
                        "Spectrum of Air Taken Using a Germanium Crystal",
                        "Spectrum of Air Taken Using a Diamond Crystal"],
                dataType=["rf", "rf", "rf"], splot=3)
fig4 = makePlot(Files4,
                Titles=["Biochar Spectra by Number of Scans"],
                dataType=["a", "a", "a"], TOver=[600, 600, 600],
                Legend=["36 Scans", "72 Scans", "1024 Scans"],
                offset=[1, 0.5025, 0], mmNorm=True)
fig5 = makePlot(Files5,
                Titles=["Biochar Spectra by Number of Scans"],
                dataType=["a", "a", "a"], TOver=[600, 600, 600],
                Legend=["Unsifted", r'>170 $\mu$m', r'80-170 $\mu$m'])

saveFig(name="Fig 2.2", folder=Chapters[1], fig=fig)
saveFig(name="Fig 2.3", folder=Chapters[1], fig=fig2)
saveFig(name="Fig 2.4", folder=Chapters[1], fig=fig3)
saveFig(name="Fig 2.5", folder=Chapters[1], fig=fig4)
saveFig(name="Fig 2.6", folder=Chapters[1], fig=fig5)

# Chapter 3
file = r"IR-Spectra\Corrected_Like_GE.0"

f = read_opus(file)

x = f.a.x
y = f.a.y

# -----------------------------
# User-provided baseline points
# -----------------------------
baseline_x = np.array([4000, 3600, 3300, 3000, 2500, 2300, 1800, 400])
baseline_y = np.array([0.154, 0.154, 0.159, 0.161, 0.159, 0.155, 0.143, 0.143])

# -----------------------------
# Build baseline by interpolation
# -----------------------------
order = np.argsort(baseline_x)
baseline_x = baseline_x[order]
baseline_y = baseline_y[order]

interp = interp1d(baseline_x, baseline_y, kind='linear',
                  fill_value="extrapolate")
bkg = interp(x)

# -----------------------------
# Corrected spectrum
# -----------------------------
y_corrected = y - bkg

# -----------------------------
# Plot: raw + baseline (top)
#       corrected spectrum (bottom)
# -----------------------------
fig, ax1 = plt.subplots(1, 1, figsize=(10, 6), sharex=True)
fig.gca().invert_xaxis()
# Top axis
ax1.plot(x, y, label="Raw Spectrum", color="Blue")
ax1.plot(x, bkg, '--', label="Calculated Baseline", linewidth=2,
         color="Orange")
ax1.scatter(baseline_x, baseline_y, color='black', zorder=5,
            label="Anchor Points")
ax1.set_title("Raw Data with Estimated Baseline")
ax1.invert_xaxis()
ax1.invert_xaxis()
ax1.set_xlabel(r'Wavenumber (cm$^{-1}$)')
ax1.set_ylabel("Intenstiy")
ax1.legend()

fig5, ax = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
plt.gca().invert_xaxis()
# Top: Baseline-corrected
ax[1].plot(x, y_corrected, color="Orange")
ax[1].invert_xaxis()
ax[1].set_ylabel("Intensity")
ax[1].set_title("Baseline Corrected Biochar Spectrum")

# Bottom: Raw
ax[0].plot(f.a.x, f.a.y, color="Blue")
ax[0].invert_xaxis()
ax[0].set_ylabel("Intensity")
ax[0].set_title("Raw Biochar Spectrum")

plt.xlabel(r'Wavenumber (cm$^{-1}$)')
plt.tight_layout()

pri_paths = [
    r"IR-Spectra\BEA0002_ATR_20260318_01.0",
    r"IR-Spectra\BEA0002_ATR_20260318_02.0",
    r"IR-Spectra\BEA0002_ATR_20260318_03.0",
]

loa_paths = [
    r"IR-Spectra\BEA0002_CO2_01_ATR_20260318_01.0",
    r"IR-Spectra\BEA0002_CO2_01_ATR_20260318_02.0",
    r"IR-Spectra\BEA0002_CO2_01_ATR_20260318_03.0",
]

pri = [read_opus(path) for path in pri_paths]
loa = [read_opus(path) for path in loa_paths]

x = pri[0].a.x

py1, py2, py3 = [pi.a.y for pi in pri]
ly1, ly2, ly3 = [lo.a.y for lo in loa]


pri_avg = (py1 + py2 + py3) / 3
loa_avg = (ly1 + ly2 + ly3) / 3

x_norm0 = 4000
x_norm1 = 1580

idx0 = np.abs(x-x_norm0).argmin()
idx1 = np.abs(x-x_norm1).argmin()

pri_y0, pri_y1 = pri_avg[idx0], pri_avg[idx1]
loa_y0, loa_y1 = loa_avg[idx0], loa_avg[idx1]

pri_avg_norm = (pri_avg - pri_y0) / (pri_y1 - pri_y0)
loa_avg_norm = (loa_avg - loa_y0) / (loa_y1 - loa_y0)

fig9, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
plt.gca().invert_xaxis()
# Top: Baseline-corrected
ax[0].plot(x, pri_avg, color="blue", label="Prisitne Biochar Spectrum")
ax[0].plot(x, loa_avg, color="orange", label="Loaded Biochar Spectrum")
ax[0].invert_xaxis()
ax[0].set_ylabel("Intensity")
ax[0].set_title("Raw Spectra")
ax[0].legend(loc='upper left')

# Bottom: Raw
ax[1].plot(x, loa_avg_norm, color="orange", label="Loaded Biochar Spectrum")
ax[1].plot(x, pri_avg_norm, color="blue", label="Pristine Biochar Spectrum")
ax[1].axvline(x[idx0], color="black", linestyle="--", linewidth=0.5)
ax[1].axvline(x[idx1], color="black", linestyle="--", linewidth=0.5)
ax[1].invert_xaxis()
ax[1].set_ylabel("Intensity")
ax[1].set_title("Normalized Spectra")
ax[1].legend(loc='upper left')

plt.xlabel(r'Wavenumber (cm$^{-1}$)')
plt.grid(alpha=0.3)

plt.tight_layout()

path_a = r"IR-Spectra\Absorbance"
peter_a = os.listdir(path_a)
pa = {}

for i in peter_a:
    # Extract sample code like 'BEA005_2p' from filename
    parts = i.split('_')
    sample_code = parts[-2] + '_' + parts[-1][:-4]
    df = pd.read_table(os.path.join(path_a, i),
                       names=['wavenumber', 'intensity_bc'], delimiter=',')
    Norm(df)
    pa[sample_code] = df

# --- Plot absorbance samples ---
fig10, ax = plt.subplots(figsize=(8, 6))

colors = ['darkred', 'orange', 'tan']
cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)
ptcolors = coloring(pa.keys())

s = 0
pt_list = ['BEA005_2p', 'BEA004_2p', 'BEA003_2p',
           'BEA002_2p', 'BEA009_2p', 'BEA001_2p']
label_list = [r'<45 $\mu$m', r'45-80 $\mu$m', r'80-170 $\mu$m',
              r'>170 $\mu$m', 'Ground', 'Original']

for i, I, l, n in zip(pt_list, ptcolors, label_list, range(len(pt_list))):
    if i not in pa:
        print(f"Skipping missing sample: {i}")
        continue
    color = cmap(n / 9.0)
    ax.plot(pa[i]['wavenumber'], pa[i]['norm'] + s, color=color, label=i)
    ax.text(300, s + 0.50, l, color=color, fontsize=10, weight='bold')
    s += 1

ax.set_title("Biochar Spectra Particle Size")
ax.set_xlim(4000, 400)
ax.set_yticks([])
ax.set_xlabel(r'Wavenumber (cm$^{-1}$)')
ax.set_ylabel(r'Normalized Absorbance')
ax.grid(True, alpha=0.3)

Files2 = [r'IR-Spectra\20231018_BEA045_c.0',
          r'IR-Spectra\BEA0001_CO_ATR_20251216_02.0']
Files3 = [r'IR-Spectra\BEA0001_CO2_01_ATRGE_20260130_01.0']
Files4 = [r'IR-Spectra\BEA0001_CO_ATR_20251216_02.0',
          r'IR-Spectra\BEA0001_CO_ATR_20251216_01Corrected.0']
Files5 = [r"IR-Spectra\BEA0002_ATR_20251216_08Cor.0",
          r"IR-Spectra\BEA0002_CO2_ATR_20251216_01Cor.0"]

fig2 = makePlot(Files2, Titles=["Raw Biochar and Aragonite Spectra"],
                dataType=["atr", "a"], Legend=["Aragonite Spectrum",
                "Biochar Spectrum"])
fig3 = makePlot(Files2, Titles=["Raw Biochar and Aragonite Spectra"],
                dataType=["atr", "a"], Legend=["Aragonite Spectrum",
                "Biochar Spectrum"], ylim=[(-0.005, 0.155)], highlight=[1900,
                                                                        2400])
fig4 = makePlot(Files3, Titles=["Raw Spectrum (Germanium Crystal)"],
                dataType=["a"])
fig6 = makePlot(Files4, Titles=["Raw Biochar Spectrum",
                                "Baseline Corrected Biochar Spectrum"],
                dataType=["a", "a"], splot=2)
fig7 = makePlot(Files5,
                Titles=[r"Biochar Spectra Before and After CO$_2$ Loading"],
                Legend=["Unexposed Biochar", r"CO$_2$ Exposed Biochar"],
                dataType=["a", "a"])
fig8 = makePlot(Files4, Titles=["Raw Spectrum", "Baseline Corrected Spectrum"],
                dataType=["a", "a"], splot=2, xlim=[(1600, 2500),
                                                    (1700, 2500)],
                ylim=[(0.06, 0.11), (-0.005, 0.02)])

saveFig(name="Fig 3.2", folder=Chapters[2], fig=fig)
saveFig(name="Fig 3.3", folder=Chapters[2], fig=fig2)
saveFig(name="Fig 3.4", folder=Chapters[2], fig=fig3)
saveFig(name="Fig 3.5", folder=Chapters[2], fig=fig4)
saveFig(name="Fig 3.6", folder=Chapters[2], fig=fig5)
saveFig(name="Fig 3.7", folder=Chapters[2], fig=fig6)
saveFig(name="Fig 3.8", folder=Chapters[2], fig=fig7)
saveFig(name="Fig 3.9", folder=Chapters[2], fig=fig8)
saveFig(name="Fig 3.10", folder=Chapters[2], fig=fig9)
saveFig(name="Fig 3.11", folder=Chapters[2], fig=fig10)
