# test_graph.py
import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("Test Graph Rendering")

# Create simple graph
G = nx.DiGraph()
G.add_node("file1.py", label="app.py", color="blue", size=30, title="Main app")
G.add_node("file2.py", label="utils.py", color="green", size=25, title="Utils")
G.add_node("func1", label="main()", color="orange", size=20, title="Main function")
G.add_edge("func1", "file1.py", color="gray", width=2)
G.add_edge("file1.py", "file2.py", color="green", width=1)

# Create network
net = Network(height="600px", width="100%", directed=True, notebook=False)
net.from_nx(G)

# Simple options
net.set_options("""
{
  "nodes": {
    "font": {
      "size": 14
    }
  },
  "physics": {
    "enabled": true
  }
}
""")

# Generate and show
html = net.generate_html()
components.html(html, height=600)

st.success("If you see a graph above, it's working!")