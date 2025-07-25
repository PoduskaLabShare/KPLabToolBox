import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""
    D Correlation Plotter
    ---
    This is a tool which will plot the 2D correlation of IR Spectra.

    -----
    """
    )
    return


@app.cell
def _():
    import gc
    import math
    import tabulate
    import numpy as np
    import marimo as mo
    import pandas as pd
    from matplotlib import colors
    import matplotlib.pyplot as plt
    from pybaselines import polynomial
    from scipy.signal import savgol_filter
    from matplotlib.gridspec import GridSpec
    from matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    return (
        GridSpec,
        colors,
        gc,
        math,
        mo,
        np,
        pd,
        plt,
        polynomial,
        savgol_filter,
    )


@app.cell
def _(
    BGC2_toggle,
    BGC_toggle,
    GridSpec,
    colors,
    contour_number,
    gc,
    math,
    mo,
    np,
    pd,
    plt,
    polynomial,
    savgol_filter,
):
    def read_data(hetero, Input_path1, Input_path2, Correlation_path):
        Input_dat1 = pd.read_csv(Input_path1, skiprows=1, header=None)
        Input_dat2 = pd.read_csv(Input_path2, skiprows=1, header=None) if hetero else None
        Corre_data = pd.read_csv(Correlation_path, header=None)
        spect1 = pd.read_csv(Input_path1, header=None)
        spect2 = pd.read_csv(Input_path2, header=None) if hetero else None

        Corre_x = Corre_data.iloc[0, 1:].astype(float).values
        Corre_y = Corre_data.iloc[1:, 0].astype(float).values
        Corre_d = Corre_data.iloc[1:, 1:].astype(float).values

        I_wav1 = Input_dat1.iloc[:, 0]
        I_val1 = Input_dat1.iloc[:, 1:]
        I_Avg1 = I_val1.mean(axis=1)

        if hetero:
            I_wav2 = Input_dat2.iloc[:, 0]
            I_val2 = Input_dat2.iloc[:, 1:]
            I_Avg2 = I_val2.mean(axis=1)
        else:
            I_wav2 = None
            I_Avg2 = None

        Correlation = [Corre_x, Corre_y, Corre_d]
        Input = [I_wav1, I_Avg1, I_wav2, I_Avg2]

        return Correlation, Input, spect1, spect2 

    def normalize(df):
        cols = df.columns[1:]
        df[cols] = (df[cols] - df[cols].min()) / (df[cols].max() - df[cols].min())
        return df

    def init_figure(title):
        fig = plt.figure(figsize=(10, 10))
        fig.suptitle(title, fontsize=16, y=0.95)

        gs = GridSpec(2, 2, width_ratios=[1, 4], height_ratios=[1, 4], hspace=0.265, wspace=0.265)

        ax_T = fig.add_subplot(gs[0, 1])
        ax_T.set_ylabel("Intensity", fontsize=12)
        ax_T.invert_xaxis()
        ax_T.set_xticks([])

        ax_L = fig.add_subplot(gs[1, 0])
        ax_L.set_xlabel("Intensity", fontsize=12)
        ax_L.invert_xaxis()
        ax_L.set_yticks([])

        ax_main = fig.add_subplot(gs[1, 1])
        ax_main.set_xlabel("Wavenumber (cm⁻¹)", labelpad=10)
        ax_main.xaxis.set_label_position('top')
        ax_main.set_ylabel("Wavenumber (cm⁻¹)")
        ax_main.invert_xaxis()
        ax_main.xaxis.set_ticks_position('top')

        def on_main_xlim_changed(ax):
            ax_T.set_xlim(ax.get_xlim())
            fig.canvas.draw_idle()

        def on_main_ylim_changed(ax):
            ax_L.set_ylim(ax.get_ylim())
            fig.canvas.draw_idle()

        ax_main.callbacks.connect('xlim_changed', on_main_xlim_changed)
        ax_main.callbacks.connect('ylim_changed', on_main_ylim_changed)

        return fig

    # def baseline_correction(df, degree=2):
    #     # print(degree_val)
    #     corrected = df.copy()
    #     x = corrected.iloc[:, 0].values

    #     for col in corrected.columns[1:]:
    #         y = corrected[col].values
    #         coeffs = np.polyfit(x, y, deg=degree)
    #         baseline = np.polyval(coeffs, x)
    #         corrected[col] = y - baseline       

    #     return corrected

    def baseline_correction(df, degree=2, mode=False):

        if mode:
            corrected = df.copy()
            x = corrected.iloc[:, 0].values

            for col in corrected.columns[1:]:
                y = corrected[col].values
                coeffs = np.polyfit(x, y, deg=degree)
                baseline = np.polyval(coeffs, x)
                corrected[col] = y - baseline  
        else:

            corrected = df.copy()

            for col in corrected.columns[1:]:
                y = corrected[col].values
                baseline, params = polynomial.modpoly(y, poly_order=degree)
                corrected[col] = y - baseline

        return corrected

    def smooth_data(df, window_length=5, polyorder=2):
        smoothed = df.copy()
        for col in smoothed.columns[1:]:
            smoothed[col] = savgol_filter(smoothed[col], window_length=window_length, polyorder=polyorder)
        return smoothed    

    def Make_Mesh(browser=None, browser2=None, Hetero=False, status=None,
                  Normalize=[], BGC=[], Smooth=[],
                  degree=[], smoothness=[], length=[]):

        paths = [browser.path(i) for i in range(len(browser.value))]

        dfs = []
        for p in paths:
            dfs.append(pd.read_csv(p, header=None))

        x_values = dfs[0].iloc[:, 0]
        y_columns = []
        for df in dfs:
            y_columns.append(df.iloc[:, 1])
        status.update(title="Combining First Spectra Set")
        combined_df = pd.concat([x_values] + y_columns, axis=1)
        combined_df.columns = [""] + list(range(1, len(paths) + 1))

        if BGC[0].value:
            status.update(title="Applying Background Correction to the First Spectra Set")
            combined_df = baseline_correction(df=combined_df, degree=degree[0], mode=BGC_toggle.value)

        if Smooth[0].value:
            status.update(title="Smoothing the First Spectra Set")
            combined_df = smooth_data(df=combined_df, window_length=length[0], polyorder=smoothness[0])

        if Normalize[0].value:
            status.update(title="Normalize First Spectra Set")
            combined_df = normalize(combined_df)

        combined_df.to_csv("Combined.csv", index=False)

        if Hetero:
            paths2 = [browser2.path(i) for i in range(len(browser2.value))]

            dfs2 = []
            for p in paths2:
                dfs2.append(pd.read_csv(p, header=None))

            x_values2 = dfs2[0].iloc[:, 0]
            y_columns2 = []
            for df in dfs2:
                y_columns2.append(df.iloc[:, 1])  
            status.update(title="Combining Second Spectra Set")
            combined_df2 = pd.concat([x_values2] + y_columns2, axis=1)
            combined_df2.columns = [""] + list(range(1, len(paths2) + 1))

            if Normalize[1].value:
                status.update(title="Normalizing Second Spectra Set")
                combined_df2 = normalize(combined_df2)

            if BGC[1].value:
                status.update(title="Applying Background Correction to the Second Spectra Set")
                combined_df2 = baseline_correction(combined_df2, degree=degree[1], mode=BGC2_toggle.value)

            if Smooth[1].value:
                status.update(title="Smoothing the Second Spectra Set")
                combined_df2 = smooth_data(combined_df2, window_length=length[1], polyorder=smoothness[1])

            combined_df2.to_csv("Combined2.csv", index=False)

        inputfile1 = "Combined.csv"
        inputfile2 = "Combined2.csv" if Hetero else inputfile1

        spec1 = pd.read_csv(inputfile1, header=0, index_col=0).T
        spec2 = pd.read_csv(inputfile2, header=0, index_col=0).T

        if len(spec1) != len(spec2):
            raise Exception(f"Data mismatching: len1 = {len(spec1)}, len2 = {len(spec2)}")

        spec1 -= spec1.mean()
        spec2 -= spec2.mean()

        status.update(title="Generating Synchronous Correlation")
        sync = pd.DataFrame(spec1.values.T @ spec2.values / (len(spec1) - 1))
        sync.index = spec1.columns
        sync.columns = spec2.columns
        sync = sync.T
        sync.to_csv("_sync.csv")

        status.update(title="Generating Hilbert Noda Matrix")
        noda = np.zeros((len(spec1), len(spec1)))
        for i in range(len(spec1)):
            for j in range(len(spec1)):
                if i != j:
                    noda[i, j] = 1 / math.pi / (j - i)

        status.update(subtitle="Generating Asynchronous Correlation")
        asyn = pd.DataFrame(spec1.values.T @ noda @ spec2.values / (len(spec1) - 1))
        asyn.index = spec1.columns
        asyn.columns = spec2.columns
        asyn = asyn.T
        asyn.to_csv("_async.csv")

    def COS_Plot(Hetero=False, Input_path1=None, Input_path2=None, Correlation_path=None, 
                 title="Untitled", colour=None, levels=3, CLines=True):

        Corre_data, Input_data, spect1, spect2 = read_data(Hetero, Input_path1, Input_path2, Correlation_path)

        fig = init_figure(title)

        ax_list = fig.get_axes()
        ax_Top, ax_Left, ax_main = ax_list

        ax_Top.plot(Input_data[0], Input_data[1], color='black', linewidth=1.5)
        ax_Top.set_xlim([Input_data[0].max(), Input_data[0].min()])
        for i in range(1, len(spect1.columns)):
            ax_Top.plot(spect1.iloc[:, 0], spect1.iloc[:, i], linestyle=":", alpha = 0.5)


        if Hetero:
            ax_Left.plot(Input_data[3], Input_data[2], color='black', linewidth=1.5)
            ax_Left.set_ylim([Input_data[2].min(), Input_data[2].max()])
            for i in range(1, len(spect2.columns)):
                ax_Left.plot(spect2.iloc[:, i], spect2.iloc[:, 0], linestyle=":",alpha = 0.5)
        else:
            ax_Left.plot(Input_data[1], Input_data[0], color='black', linewidth=1.5)
            ax_Left.set_ylim([Input_data[0].min(), Input_data[0].max()])
            for i in range(1, len(spect1.columns)):
                ax_Left.plot(spect1.iloc[:, i], spect1.iloc[:, 0], linestyle=":",alpha = 0.5)

        mesh = ax_main.contourf(Corre_data[0], Corre_data[1], Corre_data[2], levels=levels, cmap=colour)
        if CLines:
            ax_main.contour(Corre_data[0], Corre_data[1], Corre_data[2], levels=levels, colors="black", linewidths=0.5)

        x_min, x_max = Corre_data[0].min(), Corre_data[0].max()
        y_min, y_max = Corre_data[1].min(), Corre_data[1].max()
        ax_main.plot([x_min, x_max], [y_min, y_max], linestyle="--", color="black", linewidth=0.75)

        norm = colors.Normalize(vmin=-Corre_data[2].max(), vmax=Corre_data[2].max())
        cbar_ax = fig.add_axes([0.925, 0.11, 0.02, 0.545])  # [left, bottom, width, height] in figure coordinates
        cbar = fig.colorbar(mesh, cax=cbar_ax, orientation='vertical')
        fig._cbar_ax = cbar_ax 

        fig._ax_main = ax_main
        fig._Corre_data = Corre_data
        fig._contour = mesh

        return fig

    def update_plot_style(
        fig=None,
        title=None,
        label_fontsize=14,
        tick_fontsize=12,
        cmap_name='coolwarm',
        levels=contour_number.value,
        draw_contour_lines=True,
        centre=False
    ):

        ax_list = fig.get_axes()
        if len(ax_list) < 3:
            raise ValueError("Expected at least 3 axes (Top, Left, Main).")

        ax_Top, ax_Left, ax_main = ax_list[:3]

        if title:
            fig.suptitle(title, fontsize=label_fontsize + 2, x=0.625, y=0.95)

        ax_main.set_xlabel(ax_main.get_xlabel(), fontsize=label_fontsize)
        ax_main.set_ylabel(ax_main.get_ylabel(), fontsize=label_fontsize)

        for ax in [ax_Top, ax_Left, ax_main]:
            ax.tick_params(axis='both', labelsize=tick_fontsize)

        if hasattr(fig, "_Corre_data") and hasattr(fig, "_ax_main"):
            Corre_data = fig._Corre_data
            ax = fig._ax_main

            for coll in ax.collections:
                coll.remove()

            if centre == True:
                vmin = -np.max(np.abs(Corre_data[2]))
                vmax = np.max(np.abs(Corre_data[2]))

                mesh = ax.contourf(Corre_data[0], Corre_data[1], Corre_data[2],
                                    levels=levels, cmap=cmap_name, vmin=vmin, vmax=vmax)
            else:
                mesh = ax.contourf(Corre_data[0], Corre_data[1], Corre_data[2], levels=levels, cmap=cmap_name)

            if draw_contour_lines:
                ax.contour(Corre_data[0], Corre_data[1], Corre_data[2], levels=levels, colors="black", linewidths=0.5)

            if hasattr(fig, "_cbar_ax"):
                fig.delaxes(fig._cbar_ax)

            cbar_ax = fig.add_axes(fig._cbar_ax)
            cbar = fig.colorbar(mesh, cax=cbar_ax, orientation='vertical')
            cbar.set_label("Correlation Intensity", fontsize=12)

            fig._cbar_ax = cbar_ax

        fig.canvas.draw_idle()

        return fig

    def clear_cache():
        globals_to_clear = [
            "combined_df", "combined_df2",
            "dfs", "dfs2",
            "x_values", "x_values2",
            "y_columns", "y_columns2",
            "spec1", "spec2", "fig"
        ]

        for var in globals_to_clear:
            if var in globals():
                del globals()[var]

        gc.collect()
        mo.md("✅ Cleared memory and cache.")
    return COS_Plot, Make_Mesh, clear_cache, update_plot_style


@app.cell
def _(mo):
    # Toggles
    pause = mo.ui.switch(label="Pause Execution:")
    hetero_switch = mo.ui.switch(label='Toggle Hetero Spectra:')
    Normalize = mo.ui.switch(value=True, label='Normalize:')
    BGC = mo.ui.switch(value=False, label='Baseline Correct:')
    Smooth = mo.ui.switch(value=False, label='Smooth:')
    BGC_toggle = mo.ui.switch(label= "Switch to Classic BGC")
    BGC2_toggle = mo.ui.switch(label= "Switch to Classic BGC")
    return (
        BGC,
        BGC2_toggle,
        BGC_toggle,
        Normalize,
        Smooth,
        hetero_switch,
        pause,
    )


@app.cell
def _(BGC2_toggle, BGC_toggle, mo, pd):
    example = pd.DataFrame({
        "": [3999.09091, 3998.37397, 3997.65703, 3996.94009, 3996.22315, 3995.50621, 3994.78927],
        " ": [1.00000, 0.99892, 0.99827, 0.99827, 0.99876, 0.99947, 0.99355]
    })

    base_text = "Apply a baseline correction to spectra improving readability and visibility of small peaks"
    Polyorder_info = "Degree of the polynomial used for the fit (Must be less than window length) If choice is too high you may lose detail, espically for small peaks"
    wlength_info = "The number of points used to fit the polynomial (Can only be an odd integer)"
    csv_req = f"Select IR spectra to be plotted must have more than 1 .csv file with the format: (Wavenumber, Intensity) with no headers. Invalid files will cause errors."

    correction_info = mo.accordion({
        "Info" : mo.vstack([mo.md("*Here is additional infromation for each correction:*"),
                            mo.accordion({"Normalize" : mo.md("Applies a min-max normalization to the spectra"),
                                          "Baseline" : mo.vstack([mo.md(f"*{base_text}*"), mo.accordion({
                                              "degree" : mo.md("Increases the order of polynomial subtracet from backgroud")
                                            })
                                                                 ]),
                                          "Smooth" : mo.vstack([mo.md("Removes noise from the spectra by applying Savitzly-Golay Filter"),
                                                                mo.accordion({
                                                                    "Polyorder" : Polyorder_info,
                                                                    "Window Length" : wlength_info,
                                                                })

                                          ])
                                         })
                           ])

    })

    browser_info = mo.accordion({ "Info": mo.vstack([mo.md(csv_req), mo.accordion({
                                  "Example" : mo.md(example.to_markdown(index=False))
    })
                                                    ])

    })

    Advanced_mod = mo.accordion({
        "Advanced Options" : mo.hstack([BGC_toggle], justify="start")
    })

    Advanced_mod2 = mo.accordion({
        "Advanced Options" : mo.vstack([
            mo.hstack([mo.md("Spectra 1:" ), BGC_toggle], justify="start"), 
            mo.hstack([mo.md("Spectra 2:" ), BGC2_toggle], justify="start")])
    })
    return Advanced_mod, Advanced_mod2, browser_info, correction_info


@app.cell
def _(hetero_switch, mo):
    browser = mo.ui.file_browser(initial_path="", filetypes=[".csv"], multiple=True, restrict_navigation=True)

    if hetero_switch.value:
        browser2 = mo.ui.file_browser(initial_path="", filetypes=[".csv"], multiple=True, restrict_navigation=True)

    else:
        browser2 = ""

    if hetero_switch.value:
        Normalize2 = mo.ui.switch(value=True, label='Normalize:')
        BGC2 = mo.ui.switch(value=False, label='Baseline Correct:')
        Smooth2 = mo.ui.switch(value=False, label='Smooth:')

    else:
        Normalize2 = ""
        BGC2 = ""
        Smooth2 = ""
    return BGC2, Normalize2, Smooth2, browser, browser2


@app.cell
def _(mo):
    diverging_colormaps = [
        'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
        'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm',
        'bwr', 'seismic'
    ]

    title_input = mo.ui.text(value="2D-COS Plot", label="Plot Title")
    colormap_dropdown = mo.ui.dropdown(options=diverging_colormaps, label="Select colormap")

    title_fontsize = mo.ui.slider(start=10, stop=30, value=16, step=2, label="Title Font Size")
    label_fontsize = mo.ui.slider(start=8, stop=24, value=14, step=2, label="Axis Label Font Size")
    tick_fontsize = mo.ui.slider(start=6, stop=20, value=12, step=2, label="Tick Font Size")
    contour_number = mo.ui.slider(start=3, stop=12, value=3, label="Number of Contours Drawn")

    clines_switch = mo.ui.switch(value=False, label='Toggle Contour outlines:')
    asynchronous = mo.ui.switch(value=False, label='Asyncronous Plot:')
    centre = mo.ui.switch(value=True, label = 'Center Colourmap Around Zero:')
    return (
        asynchronous,
        centre,
        clines_switch,
        colormap_dropdown,
        contour_number,
        label_fontsize,
        tick_fontsize,
        title_fontsize,
        title_input,
    )


@app.cell
def _(BGC, BGC2, BGC2_toggle, BGC_toggle, Smooth, Smooth2, hetero_switch, mo):
    if Smooth.value:
        smoothness = mo.ui.slider(start=2, stop=20, label="Polyorder")
        length = mo.ui.slider(start=3, stop=35, step=2, label="Window Length")
    else: 
        smoothness = ""
        length = ""

    if BGC.value:
        if BGC_toggle.value:
            degree = mo.ui.slider(start=1, stop = 30, label="Order")
        else:
            degree = mo.ui.slider(start=1, stop = 100, label="Order")

    else:
        degree = ""

    if hetero_switch.value:
        if Smooth2.value:
            smoothness2 = mo.ui.slider(start=2, stop=20, label="Polyorder")
            length2 = mo.ui.slider(start=3, stop=35, step=2, 
                                  label="Window Length")
        else: 
            smoothness2 = ""
            length2 = ""

        if BGC2.value:
            if BGC2_toggle.value:
                degree = mo.ui.slider(start=1, stop = 30, label="Order")
            else:
                degree2 = mo.ui.slider(start=1, stop = 100, label="Order")    

        else:
            degree2 = ""

    else:
        degree2 = ""
        smoothness2 = ""
        length2 = ""

    return degree, degree2, length, length2, smoothness, smoothness2


@app.cell
def _(
    Advanced_mod,
    Advanced_mod2,
    BGC,
    BGC2,
    Normalize,
    Normalize2,
    Smooth,
    Smooth2,
    browser,
    browser2,
    browser_info,
    correction_info,
    degree,
    degree2,
    hetero_switch,
    length,
    length2,
    mo,
    pause,
    smoothness,
    smoothness2,
):
    Correct_drop = mo.accordion({
                "Apply Corrections to Spectra:": mo.vstack([
                mo.hstack([mo.md("Spectra 1:") if hetero_switch.value else mo.md(""),
                                               Normalize, BGC, degree, Smooth, smoothness, length], justify="start"),
                mo.hstack([mo.md("Spectra 2:") if hetero_switch.value else mo.md(""),
                                               Normalize2, BGC2, degree2, Smooth2, smoothness2, length2], justify="start"),
                Advanced_mod2 if hetero_switch.value else Advanced_mod,
                correction_info
                ])
                                })

    if hetero_switch.value:
       browse_drop =  mo.accordion({
                       "Select Spectra:": mo.vstack([
                           mo.hstack([
                               mo.vstack([mo.md("Fist Spectra Set:"), browser, hetero_switch]), 
                               mo.vstack([mo.md("Second Spectra Set"), browser2])
                           ]),
                           browser_info
                       ]),
       })

    else:
        browse_drop = mo.accordion({"Select Spectra:": mo.vstack([mo.md(""), browser, hetero_switch, browser_info]),

                                   })

    mo.vstack([Correct_drop, browse_drop, pause])
    return


@app.cell
def _(
    BGC,
    BGC2,
    Normalize,
    Normalize2,
    Smooth,
    Smooth2,
    degree,
    degree2,
    hetero_switch,
    length,
    length2,
    smoothness,
    smoothness2,
):
    smooth_amt = []
    wlength = []
    degree_val = []

    if Smooth.value:
        smooth_amt.append(smoothness.value)
        wlength.append(length.value)
    else:
        smooth_amt.append(None)
        wlength.append(None)

    if BGC.value:
        degree_val.append(degree.value)
    else:
        degree_val.append(None)

    if hetero_switch.value:
        if Smooth2.value:
            smooth_amt.append(smoothness2.value)
            wlength.append(length2.value)
        else:
            smooth_amt.append(None)
            wlength.append(None)

        if BGC2.value:
            degree_val.append(degree2.value)
        else:
            degree_val.append(None)


    Normalizes = [Normalize, Normalize2]
    BGCs = [BGC, BGC2]
    Smooths = [Smooth, Smooth2] 
    return BGCs, Normalizes, Smooths, degree_val, smooth_amt, wlength


@app.cell
def _(
    BGCs,
    Make_Mesh,
    Normalizes,
    Smooths,
    browser,
    browser2,
    degree_val,
    hetero_switch,
    mo,
    pause,
    smooth_amt,
    wlength,
):
    unpaused = not pause.value

    if unpaused:
        try:
            with mo.status.spinner(title="Running Correlation",  subtitle=("☕ This may take a moment... Go grab a coffee! ☕")) as spinner:
                Make_Mesh(browser=browser, browser2=browser2, Hetero=hetero_switch.value, status=spinner, Normalize=Normalizes, BGC=BGCs,
                          Smooth=Smooths, degree=degree_val, smoothness=smooth_amt, length=wlength)

            done_text = mo.md("## ✅ Mesh generation complete! ✅")
            sucess = True

        except IndexError as e:
            done_text = mo.md(f"## ⚠️ No spectra Selected! Select Spectra to generate Plot ⚠️")
            sucess = False
    else:
        done_text = None

    done_text
    return sucess, unpaused


@app.cell
def _(
    asynchronous,
    centre,
    clines_switch,
    colormap_dropdown,
    contour_number,
    fig,
    label_fontsize,
    mo,
    tick_fontsize,
    title_fontsize,
    title_input,
    update_plot_style,
):
    drawPlot = mo.ui.button(label="Draw Plot", on_click=lambda _: update_plot_style(
        fig if 'fig' in globals() else None,
        title=title_input.value,
        label_fontsize=label_fontsize.value,
        tick_fontsize=tick_fontsize.value,
        cmap_name=colormap_dropdown.value,
        levels=contour_number.value,
        draw_contour_lines=clines_switch.value,
        centre=centre.value
    ))


    mo.accordion({"Adjust Plot Output:": mo.vstack([
        title_input, colormap_dropdown, title_fontsize, label_fontsize, 
        tick_fontsize, contour_number, mo.hstack([asynchronous, clines_switch, centre], justify="start"),
        drawPlot
        ])})

    return


@app.cell
def _(clear_cache, mo):
    clear_button = mo.ui.button(label="Clear Cache", on_click=lambda _: clear_cache())


    mo.hstack([clear_button], justify="start")
    return


@app.cell
def _(COS_Plot, asynchronous, browser, hetero_switch, mo, sucess, unpaused):
    if asynchronous.value == False:
        path1 = '_sync.csv'
        path2 = 'Combined.csv'
        path3 = 'Combined2.csv'


    elif asynchronous.value == True:
        path1 = '_async.csv'
        path2 = 'Combined.csv'
        path3 = 'Combined2.csv'


    elif len(browser.value) != 0:
        path1 = None
        path2 = None
        path3 = None

    if unpaused:
        if sucess:
            fig = COS_Plot(Hetero=hetero_switch.value, title='Your Correlation Plot', Input_path1=path2, 
                            Input_path2=path3 ,Correlation_path=path1, levels=3,  colour="bwr", CLines=False)
            out = mo.mpl.interactive(fig)
            text = ""
        else:
            out = ""
            text = ""

    else:
        with open("NoPlot.png", "rb") as f:
            fig = f.read()
        text = mo.md("## Plot Execution Paused")
        out = mo.image(fig)




    mo.vstack([text, out], justify="start")

    return (fig,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
