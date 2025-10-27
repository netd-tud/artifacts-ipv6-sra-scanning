from artifacts_ipv6_sra_scanning.config import *
from tqdm.auto import tqdm
import glob

def load_and_join(files):
    df = pl.DataFrame()
    for i in tqdm(range(len(files))):
        if df.is_empty():
            df = pl.read_parquet(files[i],columns=['saddr','classification'])
            df = df.group_by("saddr").agg(classifications = pl.col("classification").unique())
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
            tmp = pl.read_parquet(files[i],columns=['saddr','classification'])
            tmp = tmp.group_by("saddr").agg(classifications = pl.col("classification").unique())
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

def run(out_file):
    tum_sra_files = glob.glob(f'{PROCESSED_DATA_DIR}/sra-vs-rand/*sra*_p0')
    tum_rand_files = glob.glob(f'{PROCESSED_DATA_DIR}/sra-vs-rand/*rand*_p0')

    tum_sra_df = load_and_join(tum_sra_files)
    tum_rand_df = load_and_join(tum_rand_files)

    total_rand = []
    total_sra = []
    echo_replies_rand = []
    echo_replies_sra = []

    for c1 in ['','_s1','_s2','_s3','_s4','_s5']:
        total_sra.append(len(tum_sra_df.filter(
                    pl.col(f'inscan{c1}')
                )))
        echo_replies_sra.append(len(tum_sra_df.filter(
                    (pl.col(f'inscan{c1}')) & (pl.col(f'code{c1}')=='echoreply')
                )))
        total_rand.append(len(tum_rand_df.filter(
                    pl.col(f'inscan{c1}')
                )))
        echo_replies_rand.append(len(tum_rand_df.filter(
                    (pl.col(f'inscan{c1}')) & (pl.col(f'code{c1}')=='echoreply')
                )))

    data = {'Random':total_rand,
            'SRA Address':total_sra,
            'Echo replies Random':echo_replies_rand,
            'Echo replies SRA':echo_replies_sra
        }
    data_df = pd.DataFrame(data)

    colors = ["#375E97", "#FB6542", "#c1195c", "#37975e"]
    linestyles = ['--','solid','-.',':']

    plt.rc("font", size=12)

    fig,ax = plt.subplots(figsize=(12*0.7,3*0.7))

    ax.plot(data_df['SRA Address'],c=colors[3],label='Any Reply (SRA)',linestyle=linestyles[1],marker='s')
    ax.plot(data_df['Echo replies SRA'],label='Echo Reply (SRA)',c=colors[3],linestyle=linestyles[0],marker='s')
    ax.plot(data_df['Random'],c=colors[2],label='Any Reply (Random)',linestyle=linestyles[1],marker='^')
    #ax.plot(data_df['Echo replies Random'],label='Echo Replies (Rand.) [#]',c=colors[2],linestyle=linestyles[0],marker='^')

    ax.set_yticks([0,2*10**7,4*10**7,6*10**7,8*10**7])
    ax.set_yticklabels([0,'20M','40M','60M','80M'])
    ax.set_ylim(0*10**7, 8*10**7)
    ax.set_xlim(-0.1,5.1)
    ax.set_xlabel('Subsequent Scan [ID]')
    ax.set_ylabel('Unique IP Addresses [#]')
    handles,labels=ax.get_legend_handles_labels()
    ax.legend(ncols=3,fontsize=11,loc='upper center',bbox_to_anchor=(0.5,1.25))
    ax.fill_between(
        data_df.index, data_df['Random'], data_df['SRA Address'], 
        interpolate=True, color="red", alpha=0.2
    )
    ax.text(4.1,7*10**7,'+ ≈10%',fontsize=11)

    plt.savefig(f'{FIGURE_DIR}/{out_file}.pdf',bbox_inches='tight')
    plt.savefig(f'{FIGURE_DIR}/{out_file}.png',dpi=200,bbox_inches='tight')

    plt.close()