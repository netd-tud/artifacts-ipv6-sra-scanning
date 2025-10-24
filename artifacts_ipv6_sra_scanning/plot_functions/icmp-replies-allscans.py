from artifacts_ipv6_sra_scanning.config import *
import seaborn as sns
import os

def load_and_prepare_df():
    file_list = [f'{PROCESSED_DATA_DIR}/scans/zmap_icmp_bgp_netaddr_1728140292_p0',
         f'{PROCESSED_DATA_DIR}/bgp48_sra_checks/zmap_icmp_bgp_48_sra_1728075185_p0',
        f'{PROCESSED_DATA_DIR}/bgp48_64s_sra_checks/zmap_icmp_bgp_48only_64s_sra_1730213648_processed',
        f'{PROCESSED_DATA_DIR}/scans/zmap_icmp_route6_64_1728147418_p0',
        f'{PROCESSED_DATA_DIR}/tuminput_sra_checks/zmap_icmp_tum_64_sra_1731694726_p0',
        ]
    pickle_path = os.path.join(INTERIM_DATA_DIR, f"all_scans_joined_cached.pkl")

    df = cv.load_or_process_pickle(pickle_path, cv.join_sra_scans, file_list)

    icmp_count = pl.concat([df.filter(pl.col('inscan')).group_by('code').agg(count=pl.col('sumreplies').sum()).with_columns(scan=pl.lit('BGP (Plain)')),
           df.filter(pl.col('inscan_s1')).group_by('code_s1').agg(count=pl.col('sumreplies_s1').sum()).with_columns(scan=pl.lit('BGP /48')).rename({'code_s1':'code'}),
           df.filter(pl.col('inscan_s2')).group_by('code_s2').agg(count=pl.col('sumreplies_s2').sum()).with_columns(scan=pl.lit('BGP /64')).rename({'code_s2':'code'}),
           df.filter(pl.col('inscan_s3')).group_by('code_s3').agg(count=pl.col('sumreplies_s3').sum()).with_columns(scan=pl.lit('Route6 /64')).rename({'code_s3':'code'}),
           df.filter(pl.col('inscan_s4')).group_by('code_s4').agg(count=pl.col('sumreplies_s4').sum()).with_columns(scan=pl.lit('Hitlist /64')).rename({'code_s4':'code'})
          ]).to_pandas()

    icmp_count = icmp_count.set_index(['code', 'scan']).squeeze().unstack('scan')
    icmp_count.index.name = None
    icmp_count = icmp_count.reindex(['echoreply','other','ambiguous'])
    icmp_count.index = ['Echo Reply','Error Msg.', 'Both']

    icmp_count['BGP (Plain)'] = icmp_count['BGP (Plain)']/icmp_count['BGP (Plain)'].sum()
    icmp_count['BGP /48'] = icmp_count['BGP /48']/icmp_count['BGP /48'].sum()
    icmp_count['BGP /64'] = icmp_count['BGP /64']/icmp_count['BGP /64'].sum()
    icmp_count['Hitlist /64'] = icmp_count['Hitlist /64']/icmp_count['Hitlist /64'].sum()
    icmp_count['Route6 /64'] = icmp_count['Route6 /64']/icmp_count['Route6 /64'].sum()
    return icmp_count

def render(out_file):
    icmp_count = load_and_prepare_df()
    plt.rc("font", size=12)
    
    fig,ax = vh.fig_ax(const.c_small_and_wide_figsize)

    sns.heatmap(icmp_count,vmin=0,vmax=1,cmap='Blues',center=0.4,annot=True,fmt='.2%',linewidth=.5,ax=ax)
    cbar = ax.collections[0].colorbar
    cbar.set_ticks([.2, .4, .6, .8, 1])
    cbar.set_ticklabels(['20%', '40%', '60%', '80%', '100%'])

    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.set_xlabel('')

    vh.save_plot(fig,out_file)
