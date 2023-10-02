from datetime import datetime
from types import NoneType
from pricing_library.node import Node
from pricing_library.market import MarketData
from pricing_library.option import Option
from pricing_library.utils import calculate_alpha


class TrinomialTree:
    n_days = 365

    def __init__(
        self,
        market: MarketData,
        option: Option,
        pricing_date: datetime,
        n_steps: int,
    ) -> None:
        """_summary_

        Args:
        ----
            market (MarketData): The MarketData object containing market informations.
            option (Option): The option associated with the trinomial tree.
            pricing_date (datetime): Pricing date of the option, could be today but must be before maturity_date.
            n_steps (int): The number of steps in the trinomial tree.
        """
        self.option = option
        self.market = market

        # calculate delta t and alpha
        assert (
            pricing_date < self.option.maturity_date
        ), "Pricing date must be before maturity date."
        self.n_steps = n_steps
        self.pricing_date = pricing_date
        self.delta_t = abs(
            ((self.option.maturity_date - pricing_date).days / n_steps) / self.n_days
        )
        self.alpha = calculate_alpha(self.market.volatility, self.delta_t)
        self.root = Node(market.spot_price, self)  # S_0...

        # current_node = self.root

        # created_steps = 0
        # while current_node.next_mid_node is None and created_steps < n_steps:
        #     current_node.compute_next_nodes()
        #     current_node = current_node.next_mid_node
        #     created_steps += 1

    def build_tree(self) -> None:
        # build from root to leaves
        # for each node, compute next generation
        # if next generation is not None, compute next generation
        # if next generation is None, stop
        current_mid = self.root
        for _ in range(self.n_steps):
            current_mid = self.contruct_next_generation(current_mid)

    def contruct_next_generation(self, prev_trunc_node: Node) -> Node:
        self.compute_next_nodes(prev_trunc_node)
        current_upper_neighbours = prev_trunc_node.node_up

        while not isinstance(current_upper_neighbours, NoneType):
            self.compute_next_nodes(current_upper_neighbours)
            current_upper_neighbours = current_upper_neighbours.node_up

        current_lower_neighbours = prev_trunc_node.node_down

        while not isinstance(current_lower_neighbours, NoneType):
            self.compute_next_nodes(current_lower_neighbours)
            current_lower_neighbours = current_lower_neighbours.node_down

        return prev_trunc_node.next_mid_node  # type: ignore

    def compute_next_nodes(self, current_node: Node) -> None:
        n = Node(current_node.forward_price, self)
        current_node.next_mid_node = n

        if isinstance(current_node.next_upper_node, NoneType):
            n_up = Node(current_node.up_price, self)
        else:
            n_up = current_node.next_upper_node

        current_node.next_upper_node = n_up

        current_node.next_upper_node.node_down = n
        n.node_up = n_up

        if isinstance(current_node.next_lower_node, NoneType):
            n_down = Node(current_node.down_price, self)
        else:
            n_down = current_node.next_lower_node
        current_node.next_lower_node = n_down

        current_node.next_lower_node.node_up = n
        n.node_down = n_down

    def compute_next_nodes(self, current_node: Node) -> None:
        n = Node(current_node.forward_price, self)
        current_node.next_mid_node = n

        if isinstance(current_node.next_upper_node, NoneType):
            n_up = Node(current_node.up_price, self)
        else:
            n_up = current_node.next_upper_node

        current_node.next_upper_node = n_up

        current_node.next_upper_node.node_down = n
        n.node_up = n_up

        if isinstance(current_node.next_lower_node, NoneType):
            n_down = Node(current_node.down_price, self)
        else:
            n_down = current_node.next_lower_node
        current_node.next_lower_node = n_down

        current_node.next_lower_node.node_up = n
        n.node_down = n_down

        # return current_node.next_mid_node

        # n = Node(fwd_price, self)
        # self.next_mid_node = n

        # n_up = Node(self.up_price, self.tree)
        # self.next_upper_node = n_up
        # n.node_up = n_up

        # n_down = Node(self.down_price, self.tree)
        # self.next_lower_node = n_down
        # n.node_down = n_down

    def __str__(self) -> str:
        return f"TrinomialTree<{self.n_steps} steps, delta_t: {self.delta_t:.3f}, alpha: {self.alpha:.3f}, root: {self.root}>"

    def __repr__(self) -> str:
        return self.__str__()
