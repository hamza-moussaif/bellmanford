import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, filedialog, ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BellmanFordApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Bellman-Ford Algorithm")
        self.master.geometry("750x700")
        self.graph = None

        # Title 
        Label(master, text="Bellman-Ford Algorithm Visualization", font=("Arial", 18), bg="lightblue").pack(fill="x", pady=10)

        # Excel button
        Button(master, text="Load Graph from Excel", command=self.load_file, font=("Arial", 14), bg="green", fg="white").pack(pady=10)

        # Source Node label and dropdown
        Label(master, text="Select Source Node:", font=("Arial", 12)).pack(pady=5)
        self.source_dropdown = ttk.Combobox(master, state="readonly", font=("Arial", 12))
        self.source_dropdown.pack(pady=5)

        # Destination Node label and dropdown
        Label(master, text="Select Destination Node:", font=("Arial", 12)).pack(pady=5)
        self.destination_dropdown = ttk.Combobox(master, state="readonly", font=("Arial", 12))
        self.destination_dropdown.pack(pady=5)

        # Run Bellman-Ford button
        Button(master, text="Run Bellman-Ford", command=self.run_bellman_ford, font=("Arial", 14), bg="Red", fg="white").pack(pady=10)

        # Visualization area (placeholder for graph canvas)
        self.figure_canvas = None

    def load_file(self):
        """Load the graph from an Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select Excel File", filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                # Read graph from Excel
                self.graph = self.read_graph_from_excel(file_path)

                # Update dropdowns with nodes
                nodes = list(self.graph.nodes)
                self.source_dropdown["values"] = nodes
                self.destination_dropdown["values"] = nodes
                self.source_dropdown.set("")  # Clear previous selection
                self.destination_dropdown.set("")
                messagebox.showinfo("Success", "Graph loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load graph: {e}")

    def read_graph_from_excel(self, file_path):
        """Read the graph from an Excel file."""
        df = pd.read_excel(file_path)
        required_columns = {"Source", "Target", "Weight"}
        if not required_columns.issubset(df.columns):
            raise ValueError("Excel file must contain columns: 'Source', 'Target', 'Weight'.")

        # Create a directed graph
        graph = nx.DiGraph()

        # Add edges and weights to the graph
        for _, row in df.iterrows():
            source, target, weight = row["Source"], row["Target"], row["Weight"]
            graph.add_edge(source, target, weight=weight)

        return graph

    def run_bellman_ford(self):
        """Run the Bellman-Ford algorithm and display results."""
        source = self.source_dropdown.get()
        destination = self.destination_dropdown.get()

        if not self.graph:
            messagebox.showerror("Error", "No graph loaded! Please load an Excel file first.")
            return
        if not source:
            messagebox.showerror("Error", "Please select a source node!")
            return
        if not destination:
            messagebox.showerror("Error", "Please select a destination node!")
            return

        try:
            # Run the Bellman-Ford algorithm
            distances, paths = self.bellman_ford(self.graph, source)

            # Show shortest distance and path
            if destination in distances:
                shortest_distance = distances[destination]
                shortest_path = paths[destination]
                messagebox.showinfo(
                    "Results",
                    f"Shortest distance from {source} to {destination}: {shortest_distance}\n"
                    f"Path: {' -> '.join(shortest_path)}"
                )
                self.draw_graph(self.graph, distances, shortest_path)
            else:
                messagebox.showwarning("No Path", f"No path exists from {source} to {destination}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def bellman_ford(self, graph, source):
        """Perform the Bellman-Ford algorithm."""
        distances = {node: float("inf") for node in graph.nodes}
        predecessors = {node: None for node in graph.nodes}
        distances[source] = 0

        # Relax edges |V| - 1 times
        for _ in range(len(graph.nodes) - 1):
            for u, v, data in graph.edges(data=True):
                weight = data["weight"]
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u

        # Check for negative weight cycles
        for u, v, data in graph.edges(data=True):
            weight = data["weight"]
            if distances[u] + weight < distances[v]:
                raise ValueError("Graph contains a negative weight cycle!")

        # Construct paths
        paths = {}
        for node in graph.nodes:
            path = []
            current = node
            while current is not None:
                path.insert(0, current)
                current = predecessors[current]
            if distances[node] != float("inf"):
                paths[node] = path

        return distances, paths

    def draw_graph(self, graph, distances, shortest_path):
        """Draw the graph with shortest path distances."""
        if self.figure_canvas:
            self.figure_canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(8, 6))
        pos = nx.circular_layout(graph)

        # Highlight the shortest path
        shortest_path_edges = list(zip(shortest_path, shortest_path[1:]))

        nx.draw(
            graph, pos, ax=ax, with_labels=True,
            node_color="lightblue", node_size=2000,
            font_size=12, font_weight="bold", edge_color="gray"
        )
        nx.draw_networkx_edges(
            graph, pos, edgelist=shortest_path_edges, edge_color="red", width=2.5, ax=ax
        )
        edge_labels = nx.get_edge_attributes(graph, "weight")
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax)

        # Annotate nodes with distances
        for node, dist in distances.items():
            x, y = pos[node]
            ax.text(x, y + 0.1, f"{dist:.2f}", fontsize=10, ha="center", color="darkred")

        ax.set_title("Graph with Shortest Path Highlighted", fontsize=16)

        # Add the graph visualization to the Tkinter GUI
        self.figure_canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.figure_canvas.get_tk_widget().pack()
        self.figure_canvas.draw()


def main():
    """Main function to start the application."""
    root = Tk()
    app = BellmanFordApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
