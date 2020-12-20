import os
import shutil
import pydot
import networkx as nx
from glob import glob
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
from .core import FUNCTION_REGISTER, Operator

class Flow(Operator):
    def __init__(self):
        super(Flow, self).__init__()

    def operate(self, inputs, output, output_root):
        print('Flow start:{}...'.format(output))
        if not os.path.exists(output):
            os.makedirs(output)
        output = os.path.join(output,'graph.png')
        graph = nx.DiGraph()
        node_dict = {}
        count = 0
        for path in inputs:
            path = path.replace(output_root, '')
            if path[0] == '/':
                path = path[1:]
            folderName = path.split('/')
            path = os.path.join(output_root, folderName[0])
            file_list = glob(path+'/*.yuv')
            if len(file_list) ==0:
                raise Exception('A yuv file should be in path:{}'.format(path))
            file_node = file_list[0]
            if not file_node in node_dict:
                node_dict.update({file_node:count})
                graph.add_node(node_dict[file_node], desc=os.path.basename(file_node))
                count += 1

            for f in folderName[1:-1]:
                pre_path = path
                path = os.path.join(path, f)
                file_list = glob(path+'/*.yuv')
                if len(file_list) ==0:
                    raise Exception('A yuv file should be in path:{}'.format(path))
                file_node = file_list[0]
                if not file_node in node_dict:
                    node_dict.update({file_node:count})
                    graph.add_node(node_dict[file_node], desc=os.path.basename(file_node))
                    count += 1
                    pre_file_list = glob(os.path.join(pre_path, '*.yuv') )
                    if len(pre_file_list) > 0:
                        pre_file_node = pre_file_list[0]
                        graph.add_edge(node_dict[pre_file_node], node_dict[file_node], name = f)
        # draw graph with labels
        plt.rcParams['figure.figsize'] = (20, 10)
        p = nx.nx_pydot.to_pydot(graph)
        p.write_dot(os.path.join(os.path.dirname(output), 'flow.dot'))
        pos = graphviz_layout(graph, prog='dot')
        nx.draw(graph, pos)
        node_labels = nx.get_node_attributes(graph, 'desc')
        nx.draw_networkx_labels(graph, pos, labels=node_labels,font_size=10)
        # edge_labels = nx.get_edge_attributes(graph, 'name')

        # nx.draw_networkx_edge_labels(graph, pos, edge_labels= edge_labels)
        x_values, y_values = zip(*pos.values())
        x_max = max(x_values)
        x_min = min(x_values)
        x_margin = (x_max - x_min)*0.5
        plt.xlim(x_min-x_margin, x_max + x_margin)
        plt.savefig(output,dpi=300)
        print('Flow finish: {}'.format(output))
        return output

FUNCTION_REGISTER('visualizationResultStage', 'Flow', Flow)