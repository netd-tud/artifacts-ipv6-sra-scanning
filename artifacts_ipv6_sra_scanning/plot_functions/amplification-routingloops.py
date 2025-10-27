from artifacts_ipv6_sra_scanning.config import *

def render(out_file):
    df_scan01 = pl.read_csv(f'{RAW_DATA_DIR}/bgp48_1728075185_routerIP_stats.csv',separator=';')
    df_scan01 = df_scan01.rename({"ASN": "AS-Number",'numamplsubnets_48':'numamplsubnets','numsubnets_48':'numsubnets','Prefix':'BGP-Prefix','routerip':'saddr'})
    
    pd_df = df_scan01.filter((pl.col('numamplsubnets')>0) & (pl.col('classification')=='timxceed')).sort('maxampl',descending=True).to_pandas()
    loop_df = df_scan01.filter((pl.col('classification')=='timxceed')).sort('numsubnets',descending=True).to_pandas()
    
    plt.rc("font", size=12)
    fig,ax = vh.fig_ax(figsize=(8*0.7,2*0.7))
    pd_df.plot(y='maxampl',ax=ax,legend=False)
    ax.set_yscale('log')
    ax.set_ylim(1,10**6)
    ax.set_xlim(-500,12000)
    ax.grid(axis='y')
    ax.set_ylabel('Amplification\n[# ICMP Repl.]')
    ax.set_xlabel('Router IP Address [Rank]')
    
    ax.set_xticks([0,2500,5000,7500,10000],['0','2.5k','5k','7.5k','10k'])
    
    ax.axvspan(-500,300,facecolor='red',alpha=0.3)
    ax.text(2000,0.1*10**4,"Amplification\n$\geq$10 (0.2%)",color='grey',horizontalalignment='center')
    vh.save_plot(fig,out_file)