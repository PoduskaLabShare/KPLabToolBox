import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""
    2D Correlation Plotter
    ---

    This is a tool which will plot the 2D correlation of IR Spectra.
    """
    )
    return


@app.cell
def _():
    import math
    import numpy as np
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    from matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    return (
        GridSpec,
        LinearSegmentedColormap,
        make_axes_locatable,
        math,
        mo,
        np,
        pd,
        plt,
    )


@app.cell
def _():



    return


@app.cell
def _(LinearSegmentedColormap):
    # Define custom colormap (Blue for low values, White near 0, Red for high values)
    RuBu = LinearSegmentedColormap.from_list("BlueWhiteRed", ["blue", "white", "red"], N=256)
    return (RuBu,)


@app.cell
def _(GridSpec, make_axes_locatable, pd, plt):
    def read_data(hetero, Input_path1, Input_path2, Correlation_path):
        Input_dat1 = pd.read_csv(Input_path1, skiprows=1, header=None)
        Input_dat2 = pd.read_csv(Input_path2, skiprows=1, header=None) if hetero else None
        Corre_data = pd.read_csv(Correlation_path, header=None)

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

        return Correlation, Input

    def normalize(df):
        # Skip the first column (wavelength) by selecting all but the first
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

        return fig

    def update_plot_style(fig, title=None, label_fontsize=14, tick_fontsize=12):
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

        fig.canvas.draw()


    def COS_Plot(hetero=False, Input_path1=None, Input_path2=None, Correlation_path=None, 
                 title="Untitled", colour=None, levels=3, CLines=True):

        # Read data
        Corre_data, Input_data = read_data(hetero, Input_path1, Input_path2, Correlation_path)

        # Initialize figure
        fig = init_figure(title)

        # Unpack subplots
        ax_list = fig.get_axes()
        ax_Top, ax_Left, ax_main = ax_list

        # Plot data
        ax_Top.plot(Input_data[0], Input_data[1], color='black', linewidth=1.5)
        ax_Top.set_xlim([Input_data[0].max(), Input_data[0].min()])

        if hetero:
            ax_Left.plot(Input_data[3], Input_data[2], color='black', linewidth=1.5)
            ax_Left.set_ylim([Input_data[2].min(), Input_data[2].max()])
        else:
            ax_Left.plot(Input_data[1], Input_data[0], color='black', linewidth=1.5)
            ax_Left.set_ylim([Input_data[0].min(), Input_data[0].max()])

        # Contour plot
        mesh = ax_main.contourf(Corre_data[0], Corre_data[1], Corre_data[2], levels=levels, cmap=colour)
        if CLines:
            ax_main.contour(Corre_data[0], Corre_data[1], Corre_data[2], levels=levels, colors="black", linewidths=0.5)

        # Diagonal line
        x_min, x_max = Corre_data[0].min(), Corre_data[0].max()
        y_min, y_max = Corre_data[1].min(), Corre_data[1].max()
        ax_main.plot([x_min, x_max], [y_min, y_max], linestyle="--", color="black", linewidth=0.75)

        # Colorbar
        divider = make_axes_locatable(ax_main)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = fig.colorbar(mesh, cax=cax, orientation='vertical')
        cbar.set_label("Correlation Intensity", fontsize=12)

        return fig  # Optional: returns fig if you want to save or further modify
    return COS_Plot, normalize, update_plot_style


@app.cell
def _(mo):
    # Toggles

    hetero_switch = mo.ui.switch(label='Toggle Hetero Spectra:')

    hetero_switch
    return (hetero_switch,)


@app.cell
def _(hetero_switch):
    hetero = hetero_switch.value
    return (hetero,)


@app.cell
def _(mo):
    browser = mo.ui.file_browser(initial_path="", filetypes=[".csv"], multiple=True)

    browser

    return (browser,)


@app.cell
def _(hetero, mo):
    if hetero == True:
        browser2 = mo.ui.file_browser(initial_path="", filetypes=[".csv"], multiple=True)

    else:
        browser2 = None

    browser2
    return (browser2,)


@app.cell
def _(browser, browser2, hetero, mo):
    if not browser.value:  # no files selected yet
        print("Waiting for input files for spectra set:")
        mo.stop(predicate=True)

    if hetero:
        if not browser2.value:  # no files selected yet
            print("Waiting for input files for second spectra set:")
            mo.stop(predicate=True)
    return


@app.cell
def _(browser, browser2, hetero, normalize, pd):
    if len(browser.value) != 0:

        # Select and sort the files from marimo file_browser (assume they're in the desired order)
        paths = [browser.path(i) for i in range(len(browser.value))]

        # Step 1: Read each CSV file
        dfs = [pd.read_csv(p, header=None) for p in paths]

        # Step 2: Extract x (from the first file) and y-values (from all files)
        x_values = dfs[0].iloc[:, 0]  # Assuming x-values are in column 0

        # Stack y-values from each file into columns
        y_columns = [df.iloc[:, 1] for df in dfs]  # Get only the y-values (excluding x-axis)

        # Step 3: Create the final DataFrame
        combined_df = pd.concat([x_values] + y_columns, axis=1)

        # Step 4: Add column headers: ["", 1, 2, 3, ...]
        column_labels = [""] + list(range(1, len(paths) + 1))
        combined_df.columns = column_labels

        # 🔄 Step 5: Normalize y-values (min-max scaling to [0, 1])
        combined_df = normalize(combined_df)

        combined_df.to_csv("Combined.csv", index=False)

        if hetero == True:
            # Select and sort the files from marimo file_browser (assume they're in the desired order)
            paths2 = [browser2.path(i) for i in range(len(browser2.value))]

            # Step 1: Read each CSV file
            dfs2 = [pd.read_csv(p, header=None) for p in paths2]

            # Step 2: Extract x (from the first file) and y-values (from all files)
            x_values2 = dfs2[0].iloc[:, 0]

            # Stack y-values from each file into columns
            y_columns2 = [df.iloc[:, 1] for df in dfs2]

            # Step 3: Create the final DataFrame
            combined_df2 = pd.concat([x_values2] + y_columns2, axis=1)

            # Step 4: Add column headers: ["", 1, 2, 3, ...]
            column_labels2 = [""] + list(range(1, len(paths2) + 1))
            combined_df2.columns = column_labels2

            # 🔄 Step 5: Normalize y-values (min-max scaling to [0, 1])
            combined_df2 = normalize(combined_df2)

            combined_df2.to_csv("Combined2.csv", index=False)
    return


@app.cell
def _(browser, hetero, math, np, pd):
    if len(browser.value) != 0:
        print(hetero)
        if hetero == False:
            inputfile1='Combined.csv'

        elif hetero == True:
            inputfile1='Combined.csv'
            inputfile2='Combined2.csv'

        left_large = True
        dynamic = True
        num_contour = 16

        # file read
        spec1 = pd.read_csv(inputfile1, header=0, index_col=0).T
        if hetero == False:
            inputfile2 = inputfile1
        spec2 = pd.read_csv(inputfile2, header=0, index_col=0).T
        if len(spec1) != len(spec2):
            raise Exception("data mismatching")
        if dynamic:
            spec1 = spec1 - spec1.mean()
            spec2 = spec2 - spec2.mean()

        # synchronous correlation
        sync = pd.DataFrame(spec1.values.T @ spec2.values / (len(spec1) - 1))
        sync.index = spec1.columns
        sync.columns = spec2.columns
        sync = sync.T
        sync.to_csv("_sync.csv")

        # Hilbert-Noda transformation matrix
        noda = np.zeros((len(spec1), len(spec1)))
        for i in range(len(spec1)):
            for j in range(len(spec1)):
                if i != j: noda[i, j] = 1 / math.pi / (j - i)

        # asynchronouse correlation
        asyn = pd.DataFrame(spec1.values.T @ noda @ spec2.values / (len(spec1) - 1))
        asyn.index = spec1.columns
        asyn.columns = spec2.columns
        asyn = asyn.T
        asyn.to_csv("_async.csv")
    return


@app.cell
def _(mo):
    title_input = mo.ui.text(value="2D-COS Plot", label="Plot Title")
    title_fontsize = mo.ui.slider(start=10, stop=30, value=16, step=2, label="Title Font Size")
    label_fontsize = mo.ui.slider(start=8, stop=24, value=14, step=2, label="Axis Label Font Size")
    tick_fontsize = mo.ui.slider(start=6, stop=20, value=12, step=2, label="Tick Font Size")
    contour_number = mo.ui.slider(start=3, stop=12, value=3, label="Number of Contours Drawn")
    clines_switch = mo.ui.switch(value=True, label='Toggle Contour outlines:')
    asynchronous = mo.ui.switch(value=False, label='Asyncronous Plot:')
    run_btn = mo.ui.button(value=0, on_click=lambda value: value + 1, label="Draw Plot")

    mo.vstack([title_input, title_fontsize, label_fontsize, tick_fontsize, contour_number, asynchronous, clines_switch, run_btn])
    return (
        asynchronous,
        clines_switch,
        contour_number,
        label_fontsize,
        run_btn,
        tick_fontsize,
        title_input,
    )


@app.cell
def _(mo, run_btn):
    if run_btn.value == 0:
        mo.stop(predicate=True)
    return


@app.cell
def _(asynchronous, browser):
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


    return path1, path2, path3


@app.cell
def _(
    COS_Plot,
    RuBu,
    clines_switch,
    contour_number,
    hetero,
    label_fontsize,
    mo,
    path1,
    path2,
    path3,
    tick_fontsize,
    title_input,
    update_plot_style,
):
    #cell
    fig = COS_Plot(hetero=hetero, title='ACBCM Biochar Correlation Plot', Input_path1=path2, 
                Input_path2=path3 ,Correlation_path=path1, levels=contour_number.value,  colour=RuBu, CLines=clines_switch.value)

    # Apply styling updates from widgets
    update_plot_style(
        fig,
        title=title_input.value,
        label_fontsize=label_fontsize.value,
        tick_fontsize=tick_fontsize.value
        )


    mo.mpl.interactive(fig) 
    return


@app.cell
def _(mo):

    import gc

    # Function to clear selected variables and force garbage collection
    def clear_cache():
        globals_to_clear = [
            "combined_df", "combined_df2",
            "dfs", "dfs2",
            "x_values", "x_values2",
            "y_columns", "y_columns2",
            "fig", "spec1", "spec2",
            "path1", "path2", "path3"
        ]

        for var in globals_to_clear:
            if var in globals():
                del globals()[var]

        gc.collect()
        mo.md("✅ Cleared memory and cache.")

    # UI Button
    clear_button = mo.ui.button(label="Clear Cache", on_click=lambda _: clear_cache())
    clear_button
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
