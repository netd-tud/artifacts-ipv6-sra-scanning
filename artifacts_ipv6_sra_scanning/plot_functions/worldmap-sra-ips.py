from artifacts_ipv6_sra_scanning.config import *


def render(out_file):
    df = pl.read_csv(f'{PROCESSED_DATA_DIR}/sources/router-ips.csv')

    shapefile = f'{DATA_DIR}/shapefiles/ne_110m_admin_0_countries.shp'
    gdf = gpd.read_file(shapefile)[["ADMIN","ADM0_A3","geometry"]]    
    gdf.columns = ["country","country_code","geometry"]    
    gdf = gdf.drop(gdf[gdf["country"]=="Antarctica"].index)
    geodata = gdf.merge(df.group_by('Geo').agg(pl.len().alias('size')).to_pandas(), left_on = 'country_code', right_on = 'Geo',how="left")
    geodata['size'] = geodata['size'].fillna(1)

    plt.rc("font", size=12)

    worldmap_figsize = (8*0.9,5*0.9)

    fig, ax = vh.fig_ax(worldmap_figsize)
    ax.axis("off")

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)

    geodata.plot(column="size", figsize=worldmap_figsize,cmap="viridis",legend=True, 
                norm=colors.LogNorm(vmin=geodata["size"].min(), vmax=geodata["size"].max()),
                legend_kwds={"label": "Router IP Addresses per Country [#]", "orientation": "horizontal","shrink":.75,'location':'bottom'},
                cax=cax,ax=ax,edgecolor='grey')

    ax.set_xlim(-160,180)
    ax.set_ylim(-60,85)

    plt.show()

    vh.save_plot(fig,'worldmap-sra-ips',autoclose=True)