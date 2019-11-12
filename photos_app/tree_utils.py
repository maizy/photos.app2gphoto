# coding: utf-8

from collections import namedtuple


class TreeNode(namedtuple('Node', ['value', 'children'])):
    pass


class Tree(namedtuple('Tree', ['root_nodes'])):
    def print(self, node_format_func=lambda x: str(x)):
        print(self.format(node_format_func))

    def _format_node_recursive(self, node, node_format_func, level):
        lines = ['   ' * level + node_format_func(node.value)]
        if node.children:
            for node in node.children:
                lines.extend(self._format_node_recursive(node, node_format_func, level + 1))
        return lines

    def format(self, node_format_func=lambda x: str(x)):
        lines = []
        for node in self.root_nodes:
            lines.extend(self._format_node_recursive(node, node_format_func, level=0))
        return '\n'.join(lines)
