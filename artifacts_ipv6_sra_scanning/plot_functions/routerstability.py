from artifacts_ipv6_sra_scanning.config import *
import glob

def load_and_join(files):
    df = pl.DataFrame()
    for i in tqdm(range(len(files))):
        if df.is_empty():
            df = pl.read_csv(files[i],columns=['saddr','classification'])
            df = df.filter(pl.col('classification')=='echoreply').select('saddr').unique()
            df = df.with_columns(inscan=True)
        else:
            tmp = pl.read_csv(files[i],columns=['saddr','classification'])
            tmp = tmp.filter(pl.col('classification')=='echoreply').select('saddr').unique()
            tmp = tmp.with_columns(inscan=True)
            df = df.join(tmp,on=['saddr'],how='full', suffix=f'_s{i}',coalesce=True)
            
    return df

def render(out_file):
    files = glob.glob(f'{PROCESSED_DATA_DIR}/stability_scans/*.log.zst')
    files.sort()
    df = load_and_join(files)
    columns = ['inscan','inscan_s2','inscan_s6','inscan_s8','inscan_s10','inscan_s11','inscan_s12']
    colors = ["#375E97", "#FB6542", "#c1195c", "#37975e"]
    linestyles = ['--','solid','-.',':']
    df = df.with_columns(sumscans=pl.sum_horizontal(['inscan','inscan_s2','inscan_s6','inscan_s8','inscan_s10','inscan_s11','inscan_s12']))
    x = [i for i in range(1,8)]
    y1 = []
    y2 = []
    y3 = []
    for column in ['inscan','inscan_s2','inscan_s6','inscan_s8','inscan_s10','inscan_s11','inscan_s12']:
        yv1 = df.filter(pl.col(column)).select('saddr').n_unique()
        y1.append(yv1)
        yv2 = df.filter((pl.col(column)) & 
                    (pl.col('sumscans')==7)).select('saddr').n_unique()
        y2.append(yv2)
    plt.rc("font", size=12)
    # If we were to simply plot pts, we'd lose most of the interesting
    # details due to the outliers. So let's 'break' or 'cut-out' the y-axis
    # into two portions - use the top (ax) for the outliers, and the bottom
    # (ax2) for the details of the majority of our data
    f, (ax, ax2) = plt.subplots(2, 1, sharex=True,figsize=(8*0.7,3*0.7),gridspec_kw={'height_ratios':[0.3,0.7]})

    # plot the same data on both axes
    ax.axhline(132571352,linestyle='--',color=colors[2],label='Scanned')
    ax2.plot(x,y1,marker='s',label='Responsive per Scan',color=colors[3])

    # zoom-in / limit the view to different portions of the data
    ax.set_ylim(129*10**6, 135*10**6)  # outliers only
    ax2.set_ylim(2*10**7,5*10**7)

    ax.set_xlim(1,7)
    ax.set_yticks([13*10**7,13.5*10**7])
    ax.set_yticklabels(['130M','135M'])

    ax.set_xticks([])
    ax2.set_xticks([1,2,3,4,5,6,7])
    # hide the spines between ax and ax2
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    #ax.xaxis.tick_top()
    ax.tick_params(labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()

    ax2.set_yticks([2*10**7,3*10**7,4*10**7,5*10**7])
    ax2.set_yticklabels(['20M','30M','40M','50M'])
    ax2.set_xlabel('Subsequent Scan [ID]')
    ax2.set_ylabel('Router IP Addresses [#]')
    h1,l1 = ax.get_legend_handles_labels()
    h2,l2 = ax2.get_legend_handles_labels()
    ax2.legend(h1+h2,l1+l2,loc='upper center',ncol=2,bbox_to_anchor=(0.5,2),framealpha=1)
    #ax2.grid(axis='y')

    ax2.yaxis.set_label_coords(-0.135, 0.8)

    #ax2.axhline(y2[0],linestyle='--',color=colors[3])
    ax2.axhspan(0,y2[0],0,8,color=colors[3], alpha=0.2)
    ax2.text(2.7,2.35*10**7,'Always responsive (21.8%)',color='grey')
    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    ax2.text(2.9,4.3*10**7,'Unresponsive (70-76%)',color='grey')

    ax2.fill_between(
        x,y1, [132571352]*7, 
        interpolate=True, color="red", alpha=0.2
    )
    ax.fill_between(
        x,y1, [132571352]*7, 
        interpolate=True, color="red", alpha=0.2
    )

    #f.subplots_adjust(hspace=0.01)
    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    plt.savefig(f'{FIGURE_DIR}/{out_file}.pdf',bbox_inches='tight')
    plt.savefig(f'{FIGURE_DIR}/{out_file}.png',dpi=200,bbox_inches='tight')

    plt.close()