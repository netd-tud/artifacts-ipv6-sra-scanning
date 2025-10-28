from artifacts_ipv6_sra_scanning.config import *

def render(out_file):
    df = pl.read_parquet(f'{PROCESSED_DATA_DIR}/sra_tum_scans_stability.parquet')

    for i in range(1, 6):
        col = f"saddr_s{i}"
        df = df.with_columns(
            pl.when(pl.col(col).is_null())
            .then(pl.lit("Unresponsive"))
            .when(pl.col(col) == pl.col("saddr"))
            .then(pl.lit("Same Address"))
            .otherwise(pl.lit("Different Address"))
            .alias(f"{col}_status")
        )
    status_cols = [f"saddr_s{i}_status" for i in range(1, 6)]

    # Melt the dataframe to long format
    df_long = df.unpivot(
        index=[],           # no id vars needed, just counts
        on=status_cols,
        variable_name="stage",
        value_name="status"
    )

    # Group by stage and status to get counts
    df_plot = df_long.group_by(["stage", "status"]).agg(
        pl.len().alias("count")
    ).sort(["stage", "count"])
    df_wide = df_plot.to_pandas().pivot(index='stage', columns='status', values='count')

    df_pct = df_wide.div(df_wide.sum(axis=1), axis=0) * 100
    df_pct = df_pct[['Same Address','Different Address','Unresponsive']]

    plt.rc("font", size=12)

    figsize = (8*0.7,3*0.7)
    fig,ax = vh.fig_ax(figsize)

    df_pct.plot(
        kind='bar', 
        stacked=True,
        color=["green","orange","gray"],
        ax=ax)
    ax.set_xlabel('Subsequent Scan [ID]')
    ax.set_ylabel('SRA Stability [%]')
    ax.set_xticks([i for i in range(0,5)],[i for i in range(1,6)],rotation=0)
    ax.set_yticks([0,25,50,75,100])
    plt.legend(ncols=3,bbox_to_anchor=(-0.18,1.26),loc='upper left',framealpha=1,fontsize=11.5,handlelength=1.5,handletextpad=0.5,columnspacing=1)
    vh.save_plot(fig,out_file)