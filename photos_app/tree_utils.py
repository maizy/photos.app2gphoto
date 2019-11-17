# coding: utf-8

from typing import Dict, Callable, Any, List


class TreeNode:
    def __init__(self, value, children=...):
        self.children: List[TreeNode] = children if children is not ... else []
        self.value = value

    def clone(self):
        return TreeNode(self.value, [c.clone() for c in self.children])

    def replace(self, match_child, new_child):
        self.children = [new_child if c == match_child else c for c in self.children]

    def insert_child_value(self, value):
        self.insert_child(TreeNode(value))

    def insert_child(self, node):
        self.children.append(node)


class Tree:
    def __init__(self, root_nodes: List[TreeNode] = ..., root_values: List[Any] = ...):
        self.root_nodes = root_nodes if root_nodes is not ... else []
        if root_values is not ...:
            self.root_nodes.extend((TreeNode(r) for r in root_values))

    def print(self, node_format_func=lambda x: str(x)):
        print(self.format(node_format_func))

    def _format_node_recursive(self, node, node_format_func, level):
        lines = ['   ' * level + node_format_func(node.value)]
        if node.children:
            for node in node.children:
                lines.extend(self._format_node_recursive(node, node_format_func, level + 1))
        return lines

    def insert_root_value(self, value):
        self.insert_root(TreeNode(value))

    def insert_root(self, node):
        self.root_nodes.append(node)

    def format(self, node_format_func=lambda x: str(x)) -> str:
        lines = []
        for node in self.root_nodes:
            lines.extend(self._format_node_recursive(node, node_format_func, level=0))
        return '\n'.join(lines)

    def traverse(self, func: Callable[[TreeNode], Any]):
        for node in self.root_nodes:
            self._traverse(func, node)

    def _traverse(self, func, node):
        func(node)
        if node.children:
            for child in node.children:
                self._traverse(func, child)

    def find_first(self, match_func: Callable[[TreeNode], Any]) -> Any:
        """
        :param match_func: return matched value or None to continue searching
        :return first matched value or None
        """
        for root in self.root_nodes:
            node_result = self._find_first(match_func, root)
            if node_result is not None:
                return node_result
        return None

    def _find_first(self, match_func, node):
        match_result = match_func(node)
        if match_result is not None:
            return match_result
        for child in node.children:
            match_result = self._find_first(match_func, child)
            if match_result is not None:
                return match_result
        return None

    def clone(self):
        new_root_node = [n.clone() for n in self.root_nodes]
        return Tree(new_root_node)


def build_index(tree: Tree, key: Callable) -> Dict[Any, TreeNode]:
    index = dict()

    def _add_to_index(node):
        index[key(node.value)] = node

    tree.traverse(_add_to_index)
    return index
