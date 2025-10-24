from artifacts_ipv6_sra_scanning.config import *
from tqdm.auto import tqdm

def concat_frames(dfs, labels, column,columns):
    if len(dfs) != len(labels):
        raise ValueError("The number of DataFrames must match the number of labels.")

    enriched_dfs = [
        df.select(columns).unique().with_columns(pl.lit(label).alias(column))
        for df, label in tqdm(zip(dfs, labels))
    ]

    return pl.concat(enriched_dfs, how="vertical")

def render(out_file):
    files = glob.glob(f'{PROCESSED_DATA_DIR}/sources/*.csv')
    dfs = [pl.scan_csv(file) for file in tqdm(files)]
    labels=['SRA','TUM Hitlist','CAIDA ITDK','RIPE Atlas','IXP Flows']
    column = 'AS-Number'
    label='ASN'
    tmp = concat_frames(dfs,labels,'source',column).collect().to_pandas()

    vh.plot_upsetplot(tmp,column,'source',labels,f'{out_file}',
                    label,title = '',bbox=(0.9,1),pickle_file=f'{INTERIM_DATA_DIR}/{out_file}.pkl',minsubsetsize='2.0%', colors=["#564F4F"]*6,
                    fontsize=10,ncols=2,legend=False)