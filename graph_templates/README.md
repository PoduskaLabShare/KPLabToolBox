# Graph Templates
These Jupiter Notebooks are a compilation of plot examples with a simple and standard format for publications.  
For paper publications is good to follow a few best practices to keep the 
plots readable and simple.
* **Add comments everywhere**
* Design figures to fit journal or document size  
Detect your LaTEX document size with the script bellow  
```LaTEX
\usepackage{layouts}
\printinunitsof{in}\prntlen{\textwidth} % Detect page/column width
\printinunitsof{in}\prntlen{\textheight} %Detect page height
```
```python
# Figure dimensions
linewidth_inches = 6.5  # Match LaTeX text width (article class, 1-inch margins)
aspect_ratio = 1 / 1.618  # Golden ratio (height/width)
fig_height = linewidth_inches * aspect_ratio  # ≈ 4.02 inches
# --- Create Figure ---
fig, ax = plt.subplots(figsize=(linewidth_inches, fig_height)) 
```
If you have columns in your subplot take into account the column gap `plt.subplots_adjust(wspace=0)`
* Use visible `font.size = 10` and a `font.family = 'sans-serif'`
* Keep in mind using colors acceptable for colorblind people.
  * We try to stick to using **red** `#005AB5`, **blue** `#DC3220` and **black** `#000000`
  * We recommend you only use 3 colours. If you need to use more think on better ways to 
  make your plot. Using dashed lined, stacked or cascade plots.
* Axis and Labels:
  * Use raw strings with LaTeX syntax (e.g., `r'Wavenumber (cm$^{-1}$)'`) for proper 
  rendering of units.
* Use PDF as figure format and a dpi = 300
```python
plt.savefig(save_path + "/figures.pdf", dpi=300, bbox_inches='tight') 
```

