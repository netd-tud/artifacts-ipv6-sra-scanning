from artifacts_ipv6_sra_scanning.config import *
import pycountry_convert as pycc
import seaborn as sns
import matplotlib.colors as mpc
import glob

def map_iso3_to_continent(cc):
    if cc=='XK' or cc=='SXM' or cc=='VAT':
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
    files = glob.glob(f'{PROCESSED_DATA_DIR}/sources/*.csv')
    files.sort()
    labels = ['SRA','Hitlist','ITDK','RIPE Atlas','IXP']

    ipinfo_asn = pl.read_parquet(f'{EXTERNAL_DATA_DIR}/ipinfo_asn.parquet')
    ipinfo_asn = ipinfo_asn.with_columns(pl.col('asn').str.replace('AS','').cast(pl.Float64))

    heatmap_data = pd.DataFrame()

    for file,label in zip(files,labels):
        tmp = pl.read_csv(file,has_header=True,new_columns=['ip-addr', 'Geo', 'AS-Number', 'BGP-Prefix', 'Org'])
        tmp = tmp.filter(pl.col('ip-addr')!='saddr')
        router_asn = tmp.select(['Geo','AS-Number','ip-addr']).unique()
        router_asn = router_asn.join(ipinfo_asn.select(['asn','type']).unique(),how='left',left_on='AS-Number',right_on='asn')
        router_asn = router_asn.group_by(['Geo','type']).agg(pl.len().alias('count')).sort('count',descending=True)
        router_asn = router_asn.filter((pl.col('Geo').is_not_null()) & (pl.col('Geo')!='ATA'))#.with_columns(pl.col("Geo").map_elements(map_iso3_to_continent, return_dtype=pl.Utf8).alias("Continent"))
        
        table = router_asn.group_by('type').agg(pl.col('count').sum().alias(label))
        order_types = ["ISP", "Hosting", "Business", "Education", "Government", "Unknown","Inactive"]
        table = table.fill_null('Unknown').with_columns(
            pl.when(pl.col("type") == "isp")
            .then(pl.lit("ISP"))  # special case
            .otherwise(
                pl.col("type").str.slice(0,1).str.to_uppercase() + pl.col("type").str.slice(1).str.to_lowercase()
            )
            .alias("type")
        ).with_columns(
            pl.col("type").map_elements(lambda x: order_types.index(x), return_dtype=pl.Int32).alias("_sort_key")
        ).sort('_sort_key').drop('_sort_key').to_pandas().set_index('type')
        if heatmap_data.empty:
            heatmap_data = table
        else:
            heatmap_data = pd.concat([heatmap_data,table],axis=1)

    heatmap_data = heatmap_data.div(heatmap_data.sum(axis=0), axis=1).mul(100).round(2).drop('Inactive',axis=0)

    figsize = (8*0.7,4*0.7)
    fig,ax = vh.fig_ax(figsize)

    annot_labels = heatmap_data.map(lambda x: f"{x:.2f}%")
    sns.heatmap(heatmap_data,fmt="",
                linecolor='white',
                cmap='YlGn',
                annot=annot_labels,
                vmin=0,
                vmax=100,
                ax=ax,
                cbar_kws={'label': 'Frequency [%]',"orientation": "vertical","shrink":1,'location':'right'})
    ax.set_ylabel('Network Type')
    ax.xaxis.tick_top()
    ax.set_xlabel('Data Source')
    ax.xaxis.set_label_position('top')

    vh.save_plot(fig,out_file)