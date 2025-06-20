'''
pip install streamlit wikipedia networkx plotly
pip installs packages
streamlit: create interactive web apps in python withou html css and js
wikipedia: python library connected to wikipedia
networkx: python library to work with graphs
plotly: gives interactive charts
'''
import streamlit as st # for building ui
import wikipedia # to fetch page data
import networkx as nx # to build graph
import plotly.graph_objects as go #make graphs interactive

st.set_page_config(layout="wide", page_title="Wikipedia Graph")
#page title
st.title(" Wikipedia Topic Explorer ")
topic = st.text_input(" Enter a Wikipedia topic")
if topic:
    try:
        st.markdown(f" Fetching links from **{topic}**...") #display message
        main_page = wikipedia.page(topic) #gets full page object
        level1_links = main_page.links[:10] # grabs first 10 hyperlinks from that page
        G = nx.Graph() # g is graph structure
        node_colors = {} #dictionary to store color of each node
        # Level 0 - Main Topic
        G.add_node(topic) #adds topic to graph
        node_colors[topic] = "green" # color of topic
        # Level 1 - Direct links
        for link in level1_links: 
            G.add_node(link)
            G.add_edge(topic, link)
            node_colors[link] = "royalblue"
            try:
                sub_page = wikipedia.page(link) #get page 
                sub_links = sub_page.links[:3]  # depth 2
                for sub_link in sub_links:
                    G.add_node(sub_link)
                    G.add_edge(link, sub_link)
                    node_colors[sub_link] = "purple"
            except:
                pass  # skip broken pages

        # layout positions
        pos = nx.spring_layout(G, seed=42)
        edge_x = []
        edge_y = []
        #loops through each edge in graph
        #gets their coordinates
        #appends them to edge_x and edge_y to prepare plotting lines between them
        #x0 and y0 starting node pos
        #x1 and y1 ending node pos
        #if none not used itll create a to b b to c c to d and a mess so used none
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
        #scatter plot
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color="#444"),
            hoverinfo='none',
            mode='lines'
        )
        #this is for drawing nodes adding texts and hover
        node_x = [] #pos of each node
        node_y = [] #pos of each node
        node_text = [] #text
        node_color = [] #colour
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            try:
                summary = wikipedia.summary(node, sentences=1) #1 line sum for each node
            except:
                summary = "No summary available."
            node_text.append(f"<b>{node}</b><br>{summary}")
            node_color.append(node_colors.get(node, "gray"))
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            textposition="top center",
            hoverinfo='text', #hover
            marker=dict(
                color=node_color,
                size=18,
                line_width=2
            ),
            text=[node for node in G.nodes()],
            hovertext=node_text
        )
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=f" Knowledge Graph for '{topic}'",
                title_font_size=22,
                showlegend=False,
                hovermode='closest',
                plot_bgcolor="#111111",
                paper_bgcolor="#111111",
                font=dict(color="white"),
                margin=dict(b=10, l=10, r=10, t=50),
                xaxis=dict(showgrid=True, zeroline=True, gridcolor="lightgray", zerolinecolor="lightgrey"),
                yaxis=dict(showgrid=True, zeroline=True, gridcolor="lightgray", zerolinecolor="lightgrey")
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        #render plot 
    except wikipedia.exceptions.DisambiguationError:
        st.warning(" Too many meanings. Be more specific.")
    except wikipedia.exceptions.PageError:
        st.error(" No such Wikipedia page found.")
    except Exception as e:
        st.error(f" Error: {e}")
        #error points
