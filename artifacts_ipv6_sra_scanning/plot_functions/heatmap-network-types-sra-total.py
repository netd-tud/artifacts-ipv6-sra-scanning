from artifacts_ipv6_sra_scanning.config import *
import pycountry_convert as pycc
import seaborn as sns
import matplotlib.colors as mpc

def map_iso3_to_continent(cc):
    if cc=='XK' or cc=='SXM':
        # kosovo is EU state, count saint marten as EU state (netherland territory)
        return 'EU'
    if cc=='UMI':
        #count umi states as US territory --> NA
        return 'NA'
    if cc=='TLS':
        # timor leste is asian state
        return 'AS'    
    alpha2 = pycc.country_alpha3_to_country_alpha2(cc)
    return pycc.country_alpha2_to_continent_code(alpha2) 

def render(out_file):
    plt.rc("font", size=10)
    ipinfo_asn = pl.read_parquet(f'{EXTERNAL_DATA_DIR}/ipinfo_asn.parquet')
    ipinfo_asn = ipinfo_asn.with_columns(pl.col('asn').str.replace('AS','').cast(pl.Float64))

    router_ips = pl.read_csv(f'{PROCESSED_DATA_DIR}/sources/01-router-ips.csv')
    router_ips = router_ips.filter(pl.col('ip-addr')!='saddr')
    router_asn = router_ips.select(['Geo','AS-Number','ip-addr']).unique()
    router_asn = router_asn.join(ipinfo_asn.select(['asn','type']).unique(),how='left',left_on='AS-Number',right_on='asn')
    router_asn = router_asn.group_by(['Geo','type']).agg(pl.len().alias('count')).sort('count',descending=True)
    router_asn = router_asn.filter((pl.col('Geo').is_not_null()) & (pl.col('Geo')!='ATA')).with_columns(
        pl.col("Geo").map_elements(map_iso3_to_continent, return_dtype=pl.Utf8).alias("Continent")
    )
    #filter antarctica values (ATA) --> only 5, not of interest and not very trustworthy imo
    router_asn = router_asn.with_columns(pl.col('type').fill_null('Unknown'))
    #remove inactive network type as their frequency is negligible with <0.001%
    counts = (
        router_asn.filter(pl.col('type')!='inactive').group_by(["Continent", "type"])
        .agg(pl.col('count').sum().alias("continent_count"))
    )

    rel_freq = (
        counts.with_columns(
            ((pl.col("continent_count") / pl.col("continent_count").sum()).mul(100).round(2).over("Continent")).alias("rel_freq")
        )
    )

    table = (
        rel_freq.pivot(
            values="rel_freq",
            index="type",
            columns="Continent"
        )
        .fill_null(0.0)  # if some combos are missing
    )
    order = counts.group_by('Continent').agg(pl.col('continent_count').sum()).sort('continent_count',descending=True).select('Continent').to_series().to_list()

    order_types = ["ISP", "Hosting", "Business", "Education", "Government", "Unknown"]
    table = table.fill_null('Unknown').with_columns(
        pl.when(pl.col("type") == "isp")
        .then(pl.lit("ISP"))  # special case
        .otherwise(
            pl.col("type").str.slice(0,1).str.to_uppercase() + pl.col("type").str.slice(1).str.to_lowercase()
        )
        .alias("type")
    ).select(['type']+order).with_columns(
        pl.col("type").map_elements(lambda x: order_types.index(x), return_dtype=pl.Int32).alias("_sort_key")
    ).sort('_sort_key').drop('_sort_key').to_pandas().set_index('type')

    figsize = (8*0.7,4*0.7)
    fig,ax = vh.fig_ax(figsize)

    annot_labels = table.map(lambda x: f"{x:.2f}%")
    sns.heatmap(table,fmt="",
                linecolor='white',
                cmap='YlGn',
                annot=annot_labels,
                vmin=0,
                vmax=100,
                ax=ax,
                cbar_kws={'label': 'Frequency [%]',"orientation": "vertical","shrink":1,'location':'right'})
    ax.xaxis.tick_top()
    ax.set_ylabel('Network Type')
    ax.set_xlabel('Continent')
    ax.xaxis.set_label_position('top')

    vh.save_plot(fig,out_file)