"""Deterministic graph layout helpers."""

from __future__ import annotations

from collections import defaultdict, deque

from PyQt6.QtCore import QPointF

from sourcetrail_remake.core.types import GraphNeighborhood, NodeId, NodeType


class GraphLayoutEngine:
    """Lay out graph neighborhoods in stable layered columns."""

    def __init__(
        self,
        *,
        layer_spacing: float = 320.0,
        node_spacing: float = 132.0,
        margin_x: float = 72.0,
        margin_y: float = 72.0,
    ) -> None:
        self.layer_spacing = layer_spacing
        self.node_spacing = node_spacing
        self.margin_x = margin_x
        self.margin_y = margin_y

    def compute_layout(self, neighborhood: GraphNeighborhood) -> dict[NodeId, QPointF]:
        nodes_by_id = {node.id: node for node in neighborhood.nodes}
        adjacency: dict[NodeId, set[NodeId]] = defaultdict(set)
        for edge in neighborhood.edges:
            adjacency[edge.source].add(edge.target)
            adjacency[edge.target].add(edge.source)

        layers = self._assign_layers(neighborhood.root_id, adjacency, tuple(nodes_by_id))
        positions: dict[NodeId, QPointF] = {}
        for layer_index in sorted(layers):
            layer_nodes = sorted(
                layers[layer_index],
                key=lambda node_id: (
                    nodes_by_id[node_id].node_type != NodeType.NODE_CLASS,
                    nodes_by_id[node_id].display_name,
                    int(node_id),
                ),
            )
            layer_height = (len(layer_nodes) - 1) * self.node_spacing
            for offset_index, node_id in enumerate(layer_nodes):
                y = self.margin_y + offset_index * self.node_spacing - (layer_height / 2)
                x = self.margin_x + layer_index * self.layer_spacing
                positions[node_id] = QPointF(x, y + 240)

        self._separate_overlaps(positions)
        return positions

    def _assign_layers(
        self,
        root_id: NodeId,
        adjacency: dict[NodeId, set[NodeId]],
        node_ids: tuple[NodeId, ...],
    ) -> dict[int, list[NodeId]]:
        depths = {root_id: 0}
        queue: deque[NodeId] = deque([root_id])
        while queue:
            current = queue.popleft()
            for neighbor in sorted(adjacency.get(current, ()), key=int):
                if neighbor in depths:
                    continue
                depths[neighbor] = depths[current] + 1
                queue.append(neighbor)

        layers: dict[int, list[NodeId]] = defaultdict(list)
        for node_id in sorted(node_ids, key=int):
            layers[depths.get(node_id, 0)].append(node_id)
        return dict(layers)

    def _separate_overlaps(self, positions: dict[NodeId, QPointF]) -> None:
        columns: dict[float, list[tuple[NodeId, QPointF]]] = defaultdict(list)
        for node_id, point in positions.items():
            columns[point.x()].append((node_id, point))

        for column in columns.values():
            column.sort(key=lambda item: (item[1].y(), int(item[0])))
            previous_y: float | None = None
            for node_id, point in column:
                if previous_y is None:
                    previous_y = point.y()
                    continue
                if point.y() - previous_y < self.node_spacing:
                    adjusted_y = previous_y + self.node_spacing
                    positions[node_id] = QPointF(point.x(), adjusted_y)
                    previous_y = adjusted_y
                    continue
                previous_y = point.y()
