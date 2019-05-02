import os
from graphviz import Digraph


def load_nodes(node_file, min_level, max_level):
    nodes = {'*': [[], [], []]}
    with open(node_file, 'r') as f:
        for line in f:
            node_content = []
            items = line.strip().split('\t')
            node_id = items[0]

            if len(items) > 1:
                lista = items[1].split(',')[:4]
                node_content.append(lista)
            else:
                node_content.append([])

            if len(items) > 2:
                listb = items[2].split(',')[:8]
                node_content.append(listb)
            else:
                node_content.append([])

            if len(items) > 3:
                listc = items[3].split(',')[:8]
                node_content.append(listc)
            else:
                node_content.append([])

            nodes[node_id] = node_content

    prune_nodes = {}
    for node_id, node_content in nodes.items():
        level = len(node_id.split('/')) - 1

        if not min_level <= level <= max_level:
            continue
        if max_level - min_level > 1 and level == min_level:
            node_content = [[], [], []]

        prune_nodes[node_id] = node_content
    return prune_nodes


def is_exact_prefix(s, prefix):
    if not s.startswith(prefix):
        return False
    tmp = s.replace(prefix, '', 1).lstrip('/')
    if '/' in tmp:
        return False
    return True


def gen_edges(nodes):
    node_ids = list(nodes.keys())
    node_ids.sort(key=lambda x: len(x))
    edges = []
    for i in range(len(nodes) - 1):
        for j in range(i + 1, len(nodes)):
            if is_parent(node_ids[i], node_ids[j]):
                edges.append([node_ids[i], node_ids[j]])
    return edges


def is_parent(node_a, node_b):
    if not node_b.startswith(node_a):
        return False
    items_a = node_a.split('/')
    items_b = node_b.split('/')
    if len(items_b) - len(items_a) == 1:
        return True
    else:
        return False


def gen_node_label(node_id, node_content, context_list):
    node_name = node_id.split('/')[-1]

    if len(node_content[0]) == 0:
        return node_name

    if len(context_list) == 1:
        if context_list[0] == "agent":
            keywords = '\\n'.join(node_content[0])
        if context_list[0] == "poi":
            keywords = '\\n'.join(node_content[1])
        if context_list[0] == "word":
            keywords = '\\n'.join(node_content[2])

        return '{%s|%s}' % (node_name, keywords)

    if len(context_list) == 3:

        keywords_feature = '\\n'.join(node_content[0])
        keywords_poi = '\\n'.join(node_content[1])
        keywords_word = '\\n'.join(node_content[2])

        return '{%s|%s|{%s|%s}}' % (node_name, keywords_feature, keywords_poi, keywords_word)


def draw(nodes, edges, output_file, context_list):
    d = Digraph(node_attr={'shape': 'record', "fontname": "PMingLiu"})
    for node_id, node_content in nodes.items():
        d.node(node_id, gen_node_label(node_id, node_content, context_list))
    for e in edges:
        d.edge(e[0], e[1])
    d.render(filename=output_file)


def main(node_file, output_file, context_list, min_level, max_level):
    nodes = load_nodes(node_file, min_level, max_level)
    print("成功生成节点")
    edges = gen_edges(nodes)
    print("成功生成连线")
    draw(nodes, edges, output_file, context_list)
    print("成功生成图片")


root_dir = ".\\2019-04-30-09-06-30"
img_dir = root_dir + '-visualization-graphviz'

prefix_list = ['*', '*/information_retrieval', '*/information_retrieval/web_search']

context_list = ["agent"]
main(img_dir + '\\results.txt', img_dir + '\\agent-1', context_list, min_level=0, max_level=1)
main(img_dir + '\\results.txt', img_dir + '\\agent-2', context_list, min_level=0, max_level=2)
main(img_dir + '\\results.txt', img_dir + '\\agent-3', context_list, min_level=0, max_level=3)

context_list = ["poi"]
main(img_dir + '\\results.txt', img_dir + '\\poi-1', context_list, min_level=0, max_level=1)
main(img_dir + '\\results.txt', img_dir + '\\poi-2', context_list, min_level=0, max_level=2)
main(img_dir + '\\results.txt', img_dir + '\\poi-3', context_list, min_level=0, max_level=3)

context_list = ["word"]
main(img_dir + '\\results.txt', img_dir + '\\word-1', context_list, min_level=0, max_level=1)
main(img_dir + '\\results.txt', img_dir + '\\word-2', context_list, min_level=0, max_level=2)
main(img_dir + '\\results.txt', img_dir + '\\word-3', context_list, min_level=0, max_level=3)

context_list = ["name", "poi", "word"]
main(img_dir + '\\results.txt', img_dir + '\\our-overall-1', context_list, min_level=0, max_level=1)
main(img_dir + '\\results.txt', img_dir + '\\our-overall-2', context_list, min_level=0, max_level=2)
main(img_dir + '\\results.txt', img_dir + '\\our-overall-3', context_list, min_level=0, max_level=3)
