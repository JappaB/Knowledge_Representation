import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pylab



def on_press(event):
    print('you pressed', event.button, event.xdata, event.ydata)





def main():

# 	G = nx.DiGraph()
# 	# fig, (ax1, ax2) = plt.subplots(2, 1)

# 	list_of_nodes = ['state1',2,'Quantity | Magnitude | Derivative \n Volume:| 0\t| -\n Inflow:  | 0\t| - \n Outflow: | 0 \t| -'
# ,4,5,6,7,8,9,10]
# 	list_of_edges = [(1,2),(2,1)]
# 	# Add nodes:
# 	G.add_nodes_from(list_of_nodes)

# 	# Add edges:
# 	G.add_edges_from(list_of_edges) #needs to be iterable

# 	nx.draw(G, with_labels=True)
# 	# cid = fig.canvas.mpl_connect('button_press_event', on_press)
# 	plt.show()


	G = nx.DiGraph()

	G.add_edges_from([('A', 'B'),('C','D'),('G','D')], weight=1)
	G.add_edges_from([('D','A'),('D','E'),('B','D'),('D','E')], weight=2)
	G.add_edges_from([('B','C'),('E','F')], weight=3)
	G.add_edges_from([('C','F')], weight=4)


	val_map = {'A': 1.0,
	                   'D': 0.5714285714285714,
	                              'H': 0.0}

	values = [val_map.get(node, 0.45) for node in G.nodes()]
	edge_labels=dict([((u,v,),d['weight'])
	                 for u,v,d in G.edges(data=True)])
	red_edges = [('C','D'),('D','A')]
	edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]

	pos=nx.spectral_layout(G, k=0.3)
	nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
	nx.draw(G,pos, node_color = values, node_size=1500,edge_color=edge_colors,edge_cmap=plt.cm.Reds)
	pylab.show()

if __name__ == '__main__':
	main()
