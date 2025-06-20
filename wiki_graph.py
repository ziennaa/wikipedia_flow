import streamlit as st
import wikipedia
import networkx as nx
import plotly.graph_objects as go
st.set_page_config(layout="wide", page_title="Wikipedia flow")
st.title(" Wikipedia Topic Explorer")
topic = st.text_input("Enter a Wikipedia topic")
if topic:
    try:
        st.markdown(f" Searching links and categories from **{topic}**")
        main_page = wikipedia.page(topic)
        summary = wikipedia.summary(topic)
        main_categories = set(main_page.categories)
        level1_links = [link for link in main_page.links if link in summary][:10]
        G = nx.Graph()
        node_colors = {}
        G.add_node(topic)
        node_colors[topic] = "green"
        for link in level1_links:
            try:
                link_page = wikipedia.page(link)
                link_categories = set(link_page.categories)
                G.add_node(link)
                G.add_edge(topic, link, label="from_summary")
                if main_categories.intersection(link_categories):
                    node_colors[link] = "deepskyblue"
                else:
                    node_colors[link] = "royalblue"
                sub_links = [sub for sub in link_page.links if sub in wikipedia.summary(link_page.title)][:3]
                for sub_link in sub_links:
                    G.add_node(sub_link)
                    G.add_edge(link, sub_link)
                    node_colors[sub_link] = "purple"
            except:
                continue
        pos = nx.spring_layout(G, seed=42)
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color="#444"),
            hoverinfo='none',
            mode='lines'
        )
        node_x, node_y, node_text, node_color = [], [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            try:
                summary = wikipedia.summary(node, sentences=1)
            except:
                summary = "No summary available."
            node_text.append(f"<b>{node}</b><br>{summary}")
            node_color.append(node_colors.get(node, "gray"))
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            textposition="top center",
            hoverinfo='text',
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
                title=f" Graph for '{topic}'",
                title_font_size=22,
                showlegend=False,
                hovermode='closest',
                plot_bgcolor="#111111",
                paper_bgcolor="#111111",
                font=dict(color="white"),
                margin=dict(b=10, l=10, r=10, t=50),
                xaxis=dict(showgrid=True, zeroline=True, gridcolor="gray", zerolinecolor="lightgray"),
                yaxis=dict(showgrid=True, zeroline=True, gridcolor="gray", zerolinecolor="lightgray")
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    except wikipedia.exceptions.DisambiguationError:
        st.warning(" Be more specific.")
    except wikipedia.exceptions.PageError:
        st.error(" No such Wikipedia page found.")
    except Exception as e:
        st.error(f"Error: {e}")
