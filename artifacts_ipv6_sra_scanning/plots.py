from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer

from artifacts_ipv6_sra_scanning.config import FIGURES_DIR, PROCESSED_DATA_DIR
from artifacts_ipv6_sra_scanning.plot_functions import *

import pkgutil
import importlib
import artifacts_ipv6_sra_scanning.plot_functions as pf

app = typer.Typer()


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    output_path: Path = FIGURES_DIR / "plot.png",
    # -----------------------------------------
):
    logger.info("Generating plots from data...")
    # Plot code is saved under plot_functions
    # each figure gets its own file with the function render()
    # all files are imported and the function render() is called
    package = pf
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_name}")
        
        # run each module if it has a run() function
        if hasattr(module, "run"):
            logger.info(f"Rendering {module_name}")
            module.run(module_name)
    logger.success("Plot generation complete.")


if __name__ == "__main__":
    app()
