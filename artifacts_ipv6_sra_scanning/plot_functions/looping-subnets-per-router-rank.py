from artifacts_ipv6_sra_scanning.config import *

def render(out_file):
    df_scan01 = pl.read_csv(f'{RAW_DATA_DIR}/bgp48_1728075185_routerIP_stats.csv',separator=';')
    df_scan01 = df_scan01.rename({"ASN": "AS-Number",'numamplsubnets_48':'numamplsubnets','numsubnets_48':'numsubnets','Prefix':'BGP-Prefix','routerip':'saddr'})
    
    loop_df = df_scan01.filter((pl.col('classification')=='timxceed')).sort('numsubnets',descending=True).to_pandas()
    
    plt.rc("font", size=12)

    fig,ax = vh.fig_ax(figsize=(8*0.7,2*0.7))
    loop_df.plot(y='numsubnets',ax=ax,legend=False)
    ax.set_yscale('log')
    ax.set_xlim(-1000,45000)
    ax.grid(axis='y')
    ax.set_ylabel('Looping /48\nsubnets [#]')
    ax.set_xlabel('Router IP Address [Rank]')

    ax.set_xticks([0,10000,20000,30000,40000],['0','10k','20k','30k','40k'])
    vh.save_plot(fig,out_file)