import tkinter as tk
from tkinter import ttk, messagebox # Importar módulos necesarios de Tkinter
import networkx as nx # Importar NetworkX para trabajar con grafos
from collections import defaultdict # Importar defaultdict para estructuras de datos
import heapq # Importar heapq para implementar el algoritmo de Dijkstra
import matplotlib # Importar matplotlib para graficar
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
         # Inicializar el grafo y otras estructuras de datos necesarias
        self.graph_dict = defaultdict(list) # Diccionario para almacenar el grafo
        self.visa_requirements = {} # Diccionario para requisitos de visa
        self.num_scales = {} # Diccionario para el número de escalas

    def add_edge(self, origin, destination, weight):
        # Método para agregar una arista al grafo
        if origin not in self.graph_dict:
            self.graph_dict[origin] = []
        if destination not in self.graph_dict:
            self.graph_dict[destination] = []
        self.graph_dict[origin].append((destination, weight))
        self.graph_dict[destination].append((origin, weight))  # Agregar la arista en ambas direcciones

    def load_visa_requirements(self, filename):
        # Método para cargar los requisitos de visa desde un archivo
        with open(filename, 'r') as file:
            for line in file:
                airport_code, destination, visa_required = line.strip().split(',')
                self.visa_requirements[airport_code] = visa_required.strip()

    def dijkstra(self, start_node, end_node, has_visa):
        # Algoritmo de Dijkstra para encontrar la ruta con el menor costo
        # Verificar requisitos de visa en el origen y destino
        if not has_visa:
            if self.visa_requirements.get(start_node, "") == "Requiere Visa":
                return "El origen requiere visa.", float('inf'), float('inf')
            if self.visa_requirements.get(end_node, "") == "Requiere Visa":
                return "El destino requiere visa.", float('inf'), float('inf')

        # Inicializar distancias y padres
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
                if not has_visa and self.visa_requirements.get(neighbor, "") == "Requiere Visa":
                    continue

                distance = current_distance + weight

                if distance < distances[neighbor]:
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

        # Actualizar el número de escalas para cada nodo en la ruta
        self.num_scales = {node: 0 for node in path}
        for i in range(1, len(path)):
            self.num_scales[path[i]] = self.num_scales[path[i-1]] + 1

        if not path or path[0] != start_node:
            return "No hay ruta disponible", float('inf'), float('inf')
        else:
            total_distance = distances[end_node]
            return path, total_distance, self.num_scales[end_node]

    def dijkstra_min_scales(self, start_node, end_node, has_visa):
        # Algoritmo de Dijkstra para encontrar la ruta con el número mínimo de escalas
        # Verificar requisitos de visa en el origen y destino
        if not has_visa:
            if self.visa_requirements.get(start_node, "") == "Requiere Visa":
                return "El origen requiere visa.", float('inf')
            if self.visa_requirements.get(end_node, "") == "Requiere Visa":
                return "El destino requiere visa.", float('inf')

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
            for neighbor, _ in self.graph_dict[current_node]:
                if not has_visa and self.visa_requirements.get(neighbor, "") == "Requiere Visa":
                    continue
                
                distance = current_distance + 1 # Siempre aumentamos en 1 el número de escalas

                if distance < distances[neighbor]:
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

        if not path or path[0] != start_node:
            return "No hay ruta disponible", float('inf')
        else:
            return path, distances[end_node]

    def show_graph(self):
        # Método para mostrar el grafo inicial
        archivo = open("caminos.txt", "r")
        added_edges = set()  # Conjunto para evitar duplicados de aristas

        for linea in archivo:
            origen, destino, peso = linea.strip().split(',')
            peso = float(peso)
            if (origen, destino) not in added_edges and (destino, origen) not in added_edges:
                self.add_edge(origen, destino, peso)
                added_edges.add((origen, destino))
        
        archivo.close()
        
        G = nx.Graph()
        for node, neighbors in self.graph_dict.items():
            for neighbor, weight in neighbors:
                G.add_edge(node, neighbor, weight=weight)

        pos = nx.spring_layout(G, k=0.05, scale=0.5)
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        min_edge_size = 1
        max_edge_size = 3
        edge_sizes = [min_edge_size + (max_edge_size - min_edge_size) * (w - min(weights)) / (max(weights) - min(weights)) for w in weights]

        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='black', width=edge_sizes, node_size=700, font_size=8)
        edge_labels = dict([((u, v,), f"{d['weight']:0.1f}") for u, v, d in G.edges(data=True)])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

class GUI:
    def __init__(self, master):
        # Método de inicialización de la interfaz gráfica
        self.master = master
        master.title("MetroTravel") # Título de la ventana principal
        self.graph = Graph() # Instancia de la clase Graph para manejar el grafo
        self.graph.show_graph() # Mostrar el grafo inicial
        self.graph.load_visa_requirements("visa_requirements.txt")  # Cargar requisitos de visa desde archivo

        city_dict = { # Diccionario para convertir códigos de aeropuerto a nombres de ciudad
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
        }

        # Crear campos de entrada para seleccionar origen y destino
        origins = list(self.graph.graph_dict.keys())
        destinations = list(self.graph.graph_dict.keys())

        city_names_origins = [f"{code} - {city_dict.get(code, code)}" for code in origins]
        city_names_destinations = [f"{code} - {city_dict.get(code, code)}" for code in destinations]

        self.start_label = tk.Label(master, text="Lugar de Origen:")
        self.start_label.grid(row=1, column=3, padx=10, pady=10)
        self.start_var = tk.StringVar()
        self.start_combobox = ttk.Combobox(master, textvariable=self.start_var, values=city_names_origins)
        self.start_combobox.grid(row=1, column=4, padx=10, pady=10)

        self.end_label = tk.Label(master, text="Lugar de Destino:")
        self.end_label.grid(row=2, column=3, padx=10, pady=10)
        self.end_var = tk.StringVar()
        self.end_combobox = ttk.Combobox(master, textvariable=self.end_var, values=city_names_destinations)
        self.end_combobox.grid(row=2, column=4, padx=10, pady=10)

        self.visa_var = tk.BooleanVar()
        self.visa_checkbox = tk.Checkbutton(master, text="¿Posee Visa?", variable=self.visa_var)
        self.visa_checkbox.grid(row=3, column=3, padx=10, pady=10)

        # Crear botones para buscar vuelos por costo mínimo y por número mínimo de escalas
        self.search_button_1 = tk.Button(master, text="Costo Mínimo", command=self.search_flights)
        self.search_button_1.grid(row=1, column=5, padx=10, pady=5)

        self.search_button_2 = tk.Button(master, text="Numero Mínimo de Escalas", command=self.search_flights_num)
        self.search_button_2.grid(row=2, column=5, padx=10, pady=5)

        # Etiqueta para mostrar los resultados de la búsqued
        self.result_label = tk.Label(master, text="")
        self.result_label.grid(row=4, column=3, columnspan=2, padx=10, pady=10)

        # Configurar el gráfico de NetworkX en un canvas de matplotlib
        self.fig = plt.figure(figsize=(7, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=10)

        self.exit_button = tk.Button(master, text="Salir", command=self.exit_app)
        self.exit_button.grid(row=3, column=5, padx=10, pady=10)

    def search_flights(self):
        # Método para buscar vuelos basado en el costo mínimo
        # Validar que se haya seleccionado un origen y destino
        if not self.start_var.get() or not self.end_var.get():
            messagebox.showwarning("Advertencia", "Debe llenar todos los campos")
            return
        
        start_node = self.start_var.get().split(" - ")[0]
        end_node = self.end_var.get().split(" - ")[0]
        has_visa = self.visa_var.get()

        # Validar que el origen y el destino no sean iguales
        if start_node == end_node:
            messagebox.showwarning("Advertencia", "Seleccione un destino distinto al origen")
            return

        path, total_distance, num_scales = self.graph.dijkstra(start_node, end_node, has_visa)

        # Mostrar el resultado en la etiqueta correspondiente
        if isinstance(path, str):
            self.result_label.configure(text=path)
        else:
            self.result_label.configure(text=f"Desde {start_node} hasta {end_node}: {' -> '.join(path)}\nLa distancia total es: {total_distance}")
        
        # Visualizar el grafo resaltando la ruta encontrada
        self.visualize_graph(path)

    #Funcion para mostrar el grafo
    def show_graph(self):
        archivo = open("caminos.txt", "r")
        added_edges = set()

        for linea in archivo:
            origen, destino, peso = linea.strip().split(',')
            peso = float(peso)
            if (origen, destino) not in added_edges and (destino, origen) not in added_edges:
                self.graph.add_edge(origen, destino, peso)
                added_edges.add((origen, destino))
        
        archivo.close()
        
        G = nx.Graph()
        for node, neighbors in self.graph.graph_dict.items():
            for neighbor, weight in neighbors:
                G.add_edge(node, neighbor, weight=weight)

        pos = nx.spring_layout(G, k=0.05, scale=0.5)
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        min_edge_size = 1
        max_edge_size = 3
        edge_sizes = [min_edge_size + (max_edge_size - min_edge_size) * (w - min(weights)) / (max(weights) - min(weights)) for w in weights]

        # Dibujar nodos con tamaño ajustado y etiquetas más pequeñas
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='black', width=edge_sizes, node_size=700, font_size=8)
        
        # Etiquetas de las aristas con fuente más pequeña
        edge_labels = dict([((u, v,), f"{d['weight']:0.1f}") for u, v, d in G.edges(data=True)])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    def search_flights_num(self):
        # Método para buscar vuelos basado en el número mínimo de escalas
        # Validar que se haya seleccionado un origen y destino
        if not self.start_var.get() or not self.end_var.get():
            messagebox.showwarning("Advertencia", "Debe llenar todos los campos")
            return
        
        start_node = self.start_var.get().split(" - ")[0]
        end_node = self.end_var.get().split(" - ")[0]
        has_visa = self.visa_var.get()

        # Validar que el origen y el destino no sean iguales
        if start_node == end_node:
            messagebox.showwarning("Advertencia", "Seleccione un destino distinto al origen")
            return

        path, num_scales = self.graph.dijkstra_min_scales(start_node, end_node, has_visa)

        if isinstance(path, str):
            self.result_label.configure(text=path)
        else:
            self.result_label.configure(text=f"Desde {start_node} hasta {end_node}: {' -> '.join(path)}\nEl número total de escalas es: {num_scales}")
        
        self.visualize_graph(path)

    def visualize_graph(self, path):
        # Método para mostrar el grafo con la ruta resaltada
        G = nx.Graph()
        for node, neighbors in self.graph.graph_dict.items():
            for neighbor, weight in neighbors:
                G.add_edge(node, neighbor, weight=weight)

        pos = nx.spring_layout(G)
        plt.clf()
        
        # Dibujar nodos con tamaño ajustado y etiquetas más pequeñas
        nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='black', width=1, node_size=700, font_size=8)
        
        if isinstance(path, list):
            nx.draw_networkx_edges(G, pos, edgelist=list(zip(path[:-1], path[1:])), edge_color='r', width=2)
        
        # Etiquetas de las aristas con fuente más pequeña
        edge_labels = dict([(edge, G[edge[0]][edge[1]]['weight']) for edge in G.edges()])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        self.canvas.draw()

    def exit_app(self):
        self.master.destroy()
        self.master.quit()


# Crear la ventana principal de la aplicación
root = tk.Tk()
gui = GUI(root)

# Mostrar el grafo inicial en la interfaz
gui.show_graph()

# Iniciar el bucle principal de la interfaz gráfica
root.mainloop()