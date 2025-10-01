from typing import Union
from .config import PROCESSED_DATA_DIR
from pathlib import Path
import polars as pl
import os
import shutil
from tqdm import tqdm
import pickle

def load_data(
    name: Union[str, list[str]],
    skip_missing: bool = False,
    default_ext: str = ".pq.zst",
    directory: Path = PROCESSED_DATA_DIR,
    **kwargs,
) -> pl.LazyFrame:
    """Read one or more files from directory in concise notation.

    Args:
        name: input file or files
        skip_missing: if True skip missing files otherwise throws an error
        default_ext: expected extension after each input filename
        directory: directory to search for files to read
        **kwargs: kwargs for pl.scan_parquet

    Returns:
        pl.LazyFrame from all input files
    """
    files = name
    if not isinstance(files, list):
        files = [name]

    files = [directory / f"{file}{default_ext}" for file in files]

    existing = [file for file in files if os.path.isfile(file)]
    if not skip_missing:
        assert len(existing) == len(
            files
        ), f"Input files missing: {set([str(file) for file in files]) - set(existing)}"

    return pl.concat([pl.scan_parquet(file, **kwargs) for file in existing])

def load_or_process_pickle(pickle_path, process_func, *args, **kwargs):
    """
    Load a DataFrame from a pickle file if it exists,
    otherwise run the processing function, save the result, and return it.

    Args:
        pickle_path: Path to the pickle file.
        process_func: Function to generate the DataFrame.
        *args, **kwargs: Arguments passed to process_func.

    Returns:
        DataFrame: The loaded or processed DataFrame.
    """
    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as f:
            return pickle.load(f)
    else:
        result = process_func(*args, **kwargs)
        with open(pickle_path, 'wb') as f:
            pickle.dump(result, f)
        return result
        
def join_sra_scans(files):
    df = pl.DataFrame()
    for i in tqdm(range(len(files))):
        if df.is_empty():
            df = pl.read_parquet(files[i],columns=['saddr','classification','numsubnets'])
            df = df.group_by("saddr").agg(classifications = pl.col("classification").unique(),
                                         sumreplies = pl.col('numsubnets').sum())
            df = df.with_columns(
                pl.when((pl.col("classifications").list.contains("echoreply")) & 
                        (pl.col("classifications").list.len() == 1))
                .then(pl.lit("echoreply"))
                .when((pl.col("classifications").list.contains("echoreply")) & 
                      (pl.col("classifications").list.len() > 1))
                .then(pl.lit("ambiguous"))
                .otherwise(pl.lit("other"))
                .alias("code")
            ).drop('classifications')
            df = df.with_columns(inscan=True)
        else:
            tmp = pl.read_parquet(files[i],columns=['saddr','classification','numsubnets'])
            tmp = tmp.group_by("saddr").agg(classifications = pl.col("classification").unique(),
                                           sumreplies = pl.col('numsubnets').sum())
            tmp = tmp.with_columns(
                pl.when((pl.col("classifications").list.contains("echoreply")) & 
                        (pl.col("classifications").list.len() == 1))
                .then(pl.lit("echoreply"))
                .when((pl.col("classifications").list.contains("echoreply")) & 
                      (pl.col("classifications").list.len() > 1))
                .then(pl.lit("ambiguous"))
                .otherwise(pl.lit("other"))
                .alias("code")
            ).drop('classifications')
            tmp = tmp.with_columns(inscan=True)
            df = df.join(tmp,on=['saddr'],how='full', suffix=f'_s{i}',coalesce=True)
    return df

def sink_parquet(df: pl.LazyFrame, path: Union[str, Path], **kwargs):
    """A wrapper for `pl.sink_parquet` that writes to `f"{path}.temp"` and then moves the file to `path`. This allows working with the existing dataset until the file is replaced

    Args:
        path: str or Path to the destination file
        **kwargs: kwargs for sink_parquet
    """
    temp_path = f"{path}.temp"
    df.sink_parquet(path=temp_path, **kwargs)
    shutil.move(temp_path, path)


def sink_parquet_scan_parquet(
    df: pl.LazyFrame, path: Union[str, Path], sink_args: dict = {}, scan_args: dict = {}
) -> pl.LazyFrame:
    """Sink parquet and subsequently scan the parquet file. This speeds up scanning times compared to working with a scan_csv file.

    Args:
        df: Dataframe to sink
        path: str or Path to destination file
        sink_args: argumenets for `cv.sink_parquet`
        scan_args: argumenets for `pl.scan_parquet`

    Returns:
        LazyFrame from scan_parquet
    """
    sink_parquet(df, path, **sink_args)
    return pl.scan_parquet(path, **scan_args)


def write_parquet(df: pl.DataFrame, path: Union[str, Path], **kwargs):
    """A wrapper for `pl.write_parquet` that writes to `f"{path}.temp"` and then moves the file to `path`. This allows working with the existing dataset until the file is replaced

    Args:
        path: str or Path to the destination file
        **kwargs: kwargs for sink_parquet
    """
    temp_path = f"{path}.temp"
    df.write_parquet(file=temp_path, **kwargs)
    shutil.move(temp_path, path)

def concat_frames(dfs: list[pl.LazyFrame], labels: list[str], column: str,columns: list[str]) -> pl.LazyFrame:
    if len(dfs) != len(labels):
        raise ValueError("The number of DataFrames must match the number of labels.")

    enriched_dfs = [
        df.select(columns).with_columns(pl.lit(label).alias(column))
        for df, label in zip(dfs, labels)
    ]

    return pl.concat(enriched_dfs, how="vertical")