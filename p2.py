import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
from collections import defaultdict
import heapq
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.graph_dict = {}
        self.graph_dict_1 = {}
        self.visa_requirements = {}
        self.num_scales = {}

    def add_edge(self, origin, destination, weight):
        if origin not in self.graph_dict:
            self.graph_dict[origin] = []
            self.visa_requirements[origin] = False  
        if destination not in self.graph_dict:
            self.graph_dict[destination] = []
            self.visa_requirements[destination] = True 
        self.graph_dict[origin].append((destination, weight))

    def dijkstra(self, start_node, end_node, has_visa):
        # Inicializar las distancias y los padres
        distances = {node: float('inf') for node in self.graph_dict}
        distances[start_node] = 0
        parents = {node: None for node in self.graph_dict}
        pq = [(0, start_node)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == end_node:
                break

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.graph_dict[current_node]:
                distance = current_distance + weight

                if distance < distances[neighbor] and (has_visa or not self.visa_requirements[(current_node, neighbor)]):
                    distances[neighbor] = distance
                    parents[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        # Reconstruir la ruta
        path = []
        node = end_node
        while node is not None:
            path.append(node)
            node = parents[node]
        path.reverse()

        # Actualizar el número de escalas de cada nodo en el camino
        self.num_scales = {node: 0 for node in path}
        for i in range(1, len(path)):
            self.num_scales[path[i]] = self.num_scales[path[i-1]] + 1

        if not path or path[0] != start_node:
            return "No hay ruta disponible", float('inf'), float('inf')
        else:
            total_distance = distances[end_node]
            return path, total_distance, self.num_scales[end_node]
        
    
    #Mostrat el grafo el matpotlib leyendo el txt caminos.txt
    def show_graph(self):
        archivo = open("caminos.txt", "r")
        for linea in archivo:
            origen, destino, peso = linea.strip().split(',')
            self.add_edge(origen, destino, float(peso))
        archivo.close()
        G = nx.Graph()
        for node, neighbors in self.graph_dict.items():
            for neighbor, weight in neighbors:
                G.add_edge(node, neighbor, weight=weight)
   
class GUI:
    def __init__(self, master):
        self.master = master
        master.title("MetroTravel")

        self.graph = Graph()
        self.graph.show_graph()

        city_dict = {
            "CCS": "Caracas",
            "AUA": "Aruba",
            "CUR": "Curazao",
            "BON": "Bonaire",
            "SXM": "Sint Maarten",
            "SDQ": "Santo Domingo",
            "SBH": "San Bartolomé",
            "POS": "Puerto España",
            "BGI": "Barbados",
            "PTP": "Pointe-à-Pitre",
            "FDF": "Fort-de-France"
            # Añade más asociaciones según sea necesario
        }


        # Add edges to the graph
        archivo = open("caminos.txt", "r")
        for linea in archivo:
            origen, destino, peso = linea.strip().split(',')
            self.graph.add_edge(origen, destino, float(peso))
        archivo.close()
        # Create input fields
        origins = []
        destinations = []

        archivo = open("caminos.txt", "r")
        for linea in archivo:
            origen, destino, peso = linea.strip().split(',')
            if origen not in origins:
                origins.append(origen)
            if destino not in destinations:
                destinations.append(destino)
        archivo.close()

        city_names_origins = [f"{code} - {city_dict.get(code, code)}" for code in origins]
        city_names_destinations = [f"{code} - {city_dict.get(code, code)}" for code in destinations]

        self.start_label = tk.Label(master, text="Start Node:")
        self.start_label.grid(row=0, column=0, padx=10, pady=10)
        self.start_var = tk.StringVar()
        self.start_combobox = ttk.Combobox(master, textvariable=self.start_var, values=city_names_origins)
        self.start_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.end_label = tk.Label(master, text="End Node:")
        self.end_label.grid(row=1, column=0, padx=10, pady=10)
        self.end_var = tk.StringVar()
        self.end_combobox = ttk.Combobox(master, textvariable=self.end_var, values=city_names_destinations)
        self.end_combobox.grid(row=1, column=1, padx=10, pady=10)

        self.visa_var = tk.BooleanVar()
        self.visa_checkbox = tk.Checkbutton(master, text="I have a visa", variable=self.visa_var)
        self.visa_checkbox.grid(row=2, column=0, padx=10, pady=10)

        # Create the button
        self.search_button_1 = tk.Button(master, text="Costo minimo", command=self.search_flights)
        self.search_button_1.grid(row=2, column=1, padx=10, pady=5)

        self.search_button_2 = tk.Button(master, text="Numero minimo de escalas", command=self.search_flights_num)
        self.search_button_2.grid(row=3, column=1, padx=10, pady=5)

        # Create the result label
        self.result_label = tk.Label(master, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Create the graph canvas
        self.fig = plt.figure(figsize=(7, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=5, column=2, rowspan=4)

        #Aqui construyo el grafo completo al ejecutarse el programa
        self.graph = Graph()
        self.graph.show_graph()


        self.visa_var = tk.BooleanVar()
        self.visa_checkbox = tk.Checkbutton(master, text="I have a visa", variable=self.visa_var)
        self.visa_checkbox.grid(row=2, column=0, padx=10, pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=self.exit_app)
        self.exit_button.grid(row=5, column=1, padx=10, pady=10)

    #Funcion para mostrar el grafo
    def show_graph(self):
        archivo = open("caminos.txt", "r")
        for linea in archivo:
            origen, destino, peso = linea.strip().split(',')
            self.graph.add_edge(origen, destino, float(peso))
        archivo.close()
        G = nx.Graph()
        for node, neighbors in self.graph.graph_dict.items():
            for neighbor, weight in neighbors:
                G.add_edge(node, neighbor, weight=weight)
        pos = nx.spring_layout(G, k=0.05, scale=0.5)
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        min_edge_size = 2
        max_edge_size = 6
        edge_sizes = [min_edge_size + (max_edge_size - min_edge_size) * (w - min(weights)) / (max(weights) - min(weights)) for w in weights]
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', width=edge_sizes)
        font_size = 8
        edge_labels = dict([((u, v,), f"{d['weight']:0.1f}") for u, v, d in G.edges(data=True)])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,font_size=font_size)

    def search_flights(self):
        # Valido que coloquen algo en los textboxes
        if not self.start_var.get() or not self.end_var.get():
            messagebox.showwarning("Advertencia", "Debe llenar todos lo campos")
            return

        start_node = self.start_var.get().split(" - ")[0]
        end_node = self.end_var.get().split(" - ")[0]
        has_visa = self.visa_var.get()

        # Check if a visa is required for the destination
        if not has_visa and self.graph.visa_requirements[end_node]:
            self.result_label.configure(text=f"You need a visa to travel to {end_node}")
            return

        path, total_distance, num_scales = self.graph.dijkstra(start_node, end_node, has_visa)

        if isinstance(path, str):
            self.result_label.configure(text=path)
        else:
            self.result_label.configure(text=f"The shortest path from {start_node} to {end_node} is: {' -> '.join(path)}\nThe total distance is: {total_distance}")
        # Visualize the graph
        G = nx.Graph()
        for node, neighbors in self.graph.graph_dict.items():
            for neighbor, weight in neighbors:
                G.add_edge(node, neighbor, weight=weight)
        
        pos = nx.spring_layout(G)
        plt.clf()
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', width=2)
        nx.draw_networkx_edges(G, pos, edgelist=list(zip(path[:-1], path[1:])), edge_color='r', width=3)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=dict([(edge, G[edge[0]][edge[1]]['weight']) for edge in G.edges()]))
        self.canvas.draw()
    def search_flights_num(self):
        # Valido que coloquen algo en los textboxes
        if not self.start_var.get() or not self.end_var.get():
            messagebox.showwarning("Advertencia", "Debe llenar todos lo campos")
            return
        start_node = self.start_var.get().split(" - ")[0]
        end_node = self.end_var.get().split(" - ")[0]
        has_visa = self.visa_var.get()

        # Check if a visa is required for the destination
        if not has_visa and self.graph.visa_requirements[end_node]:
            self.result_label.configure(text=f"You need a visa to travel to {end_node}")
            return

        path, total_distance, num_scales = self.graph.dijkstra(start_node, end_node, has_visa)

        if isinstance(path, str):
            self.result_label.configure(text=path)
        else:
            self.result_label.configure(text=f"The minimum number of scales is: {num_scales}")

            # Visualizar el grafo
            G = nx.Graph()
            for node, neighbors in self.graph.graph_dict.items():
                for neighbor, weight in neighbors:
                    G.add_edge(node, neighbor, weight=weight)

            pos = nx.spring_layout(G)
            plt.clf()
            nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', width=2)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=dict([(edge, G[edge[0]][edge[1]]['weight']) for edge in G.edges()]))
            self.canvas.draw()
    def exit_app(self):
        self.master.destroy()
        self.master.quit()


root = tk.Tk()
gui = GUI(root)
gui.show_graph()
root.mainloop()