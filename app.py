import gradio as gr
import asyncio
import plotly.graph_objects as go
import h3
from src.trackemdown.core import fetch_geotags

def create_map(results):
    """Create an interactive map showing the geotag locations and hexagon boundaries"""
    if not results:
        return go.Figure()

    lats = [result.latitude for result in results]
    lons = [result.longitude for result in results]
    addresses = [result.address for result in results]
    geotags = [result.geotag for result in results]

    fig = go.Figure()

    # Add hexagon boundaries for each geotag
    colors = ['blue', 'green', 'purple', 'orange', 'brown', 'pink', 'gray', 'olive', 'cyan', 'magenta']

    for i, geotag in enumerate(geotags):
        try:
            # Get hexagon boundary coordinates
            boundary = h3.cell_to_boundary(geotag)

            # Convert to lat/lon lists (boundary returns (lat, lon) tuples)
            hex_lats = [coord[0] for coord in boundary] + [boundary[0][0]]  # Close the polygon
            hex_lons = [coord[1] for coord in boundary] + [boundary[0][1]]

            # Add hexagon outline
            fig.add_trace(go.Scattermap(
                lat=hex_lats,
                lon=hex_lons,
                mode='lines',
                line=dict(width=2, color=colors[i % len(colors)]),
                name=f"H3 Hexagon {i+1}",
                hovertemplate=f'<b>H3 Geotag: {geotag}</b><extra></extra>',
                showlegend=True
            ))

        except Exception as e:
            print(f"Could not draw hexagon for {geotag}: {e}")

    # Add location markers
    fig.add_trace(go.Scattermap(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(size=8, color='red'),
        text=[f"{addr}<br>Geotag: {geotag}" for addr, geotag in zip(addresses, geotags)],
        hovertemplate='<b>%{text}</b><extra></extra>',
        name="Locations",
        showlegend=True
    ))

    fig.update_layout(
        map=dict(
            style="open-street-map",
            zoom=2,
            center=dict(lat=lats[0], lon=lons[0]) if lats else dict(lat=0, lon=0)
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(x=0.02, y=0.98)
    )

    return fig

async def get_geotags_async(query: str, resolution: int):
    try:
        results = await fetch_geotags(query, resolution)

        # Format results for table display
        formatted_results = []
        for result in results:
            formatted_results.append([
                result.address,
                f"{result.latitude:.6f}",
                f"{result.longitude:.6f}",
                result.geotag
            ])

        # Create map
        map_fig = create_map(results)

        return formatted_results, map_fig, gr.update(visible=False)

    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        return [], empty_fig, gr.update(value=f"Error: {str(e)}", visible=True)

def get_geotags(query: str, resolution: int):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_geotags_async(query, resolution))
    finally:
        loop.close()

# H3 Resolution levels:
# 0: ~4,250 km hexagons (continent scale)
# 5: ~252 km hexagons (large city scale)
# 9: ~0.1 km hexagons (neighborhood scale)
# 12: ~0.01 km hexagons (building scale)
# 15: ~0.0005 km hexagons (room scale) - highest resolution

with gr.Blocks() as demo:
    gr.Markdown("# TrackEmDown")

    with gr.Row():
        query_input = gr.Textbox(label="Address or Coordinates")
        resolution_input = gr.Number(label="H3 Resolution", value=15, minimum=0, maximum=15)

    search_btn = gr.Button("Generate Geotags")

    results_table = gr.Dataframe(
        headers=["Address", "Latitude", "Longitude", "H3 Geotag"],
        datatype=["str", "str", "str", "str"],
        interactive=False,
        wrap=True
    )

    map_plot = gr.Plot(label="Map View")

    error_output = gr.Textbox(label="Error", lines=3, interactive=False, visible=False)

    search_btn.click(
        fn=get_geotags,
        inputs=[query_input, resolution_input],
        outputs=[results_table, map_plot, error_output]
    )

if __name__ == "__main__":
    demo.launch(share=False)
