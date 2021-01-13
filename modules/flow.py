import os
import shutil
import pydot
import networkx as nx
from glob import glob
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.lines import Line2D
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
from .core import FUNCTION_REGISTER, Operator

class Flow(Operator):
    def __init__(self):
        super(Flow, self).__init__()
        self.edge_type_list = ['downFrameRateStage','downResolutionStage', 'encodingStage',
                            'upResolutionStage','upFrameRateStage', 'analyzerStage']
        jet = plt.get_cmap('tab10')
        cNorm = colors.Normalize(vmin=0, vmax=len(self.edge_type_list))
        self.scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

    def stageType2Color(self, stageType):
        for t in self.edge_type_list:
            if t in stageType:
                idx = self.edge_type_list.index(t)
                break
        color = self.scalarMap.to_rgba(idx)
        return color
    def draw_graph(self, graph, output, numInputs):
        # draw graph with labels
        r = numInputs/4
        w,h = max(20, r*20), max(5, r*5)
        plt.rcParams['figure.figsize'] = (w, h)
        p = nx.nx_pydot.to_pydot(graph)
        p.write_dot(os.path.join(os.path.dirname(output), 'flow.dot'))
        pos = graphviz_layout(graph, prog='dot')
        node_colors = nx.get_node_attributes(graph, 'node_color')
        nx.draw_networkx_nodes(graph, pos, node_color=[v for k,v in node_colors.items()], alpha=0.5)
        edge_colors = nx.get_edge_attributes(graph, 'edge_color')
        nx.draw_networkx_edges(graph, pos, edge_color=[v for k,v in edge_colors.items()])
        
        
        node_labels = nx.get_node_attributes(graph, 'desc')
        nx.draw_networkx_labels(graph, pos, labels=node_labels,font_size=11)
        # edge_labels = nx.get_edge_attributes(graph, 'name')

        # nx.draw_networkx_edge_labels(graph, pos, edge_labels= edge_labels)
        x_values, y_values = zip(*pos.values())
        x_max = max(x_values)
        x_min = min(x_values)
        if x_min != x_max:
            x_margin = (x_max - x_min)*0.25
            plt.xlim(x_min-x_margin, x_max + x_margin)
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0,hspace=0, wspace=0)
        proxies = [Line2D([0,1], [0,1], color=self.scalarMap.to_rgba(i), lw=5) for i in range(len(self.edge_type_list))]
        plt.legend(proxies, self.edge_type_list)
        plt.savefig(output,dpi=200)

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
                color = "red"
                graph.add_node(node_dict[file_node], desc=os.path.basename(file_node), node_color=color)
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
                    color = self.stageType2Color(f)
                    desc = os.path.basename(file_node)
                    desc = desc.replace('fps_','fps\n_') if 'bpp' in desc else desc
                    graph.add_node(node_dict[file_node], desc=desc, node_color=color)
                    count += 1
                    pre_file_list = glob(os.path.join(pre_path, '*.yuv') )
                    if len(pre_file_list) > 0:
                        pre_file_node = pre_file_list[0]
                        color = self.stageType2Color(f)
                        graph.add_edge(node_dict[pre_file_node], node_dict[file_node], name = f, edge_color=color)
        self.draw_graph(graph, output, len(inputs))
        print('Flow finish: {}'.format(output))
        return graph

FUNCTION_REGISTER('visualizationResultStage', 'Flow', Flow)