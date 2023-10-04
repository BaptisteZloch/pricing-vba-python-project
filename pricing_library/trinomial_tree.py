from datetime import datetime
from types import NoneType
from pricing_library.node import Node
from pricing_library.market import MarketData
from pricing_library.option import Option
from pricing_library.utils import calculate_alpha, calculate_discount_factor


class TrinomialTree:
    n_days = 365

    def __init__(
        self,
        market: MarketData,
        pricing_date: datetime,
        n_steps: int,
    ) -> None:
        """Constructor of the TrinomialTree class.

        Args:
        ----
            market (MarketData): The MarketData object containing market informations.
            pricing_date (datetime): Pricing date of the option, could be today but must be before maturity_date.
            n_steps (int): The number of steps in the trinomial tree.
        """
        # self.option = option
        self.market = market

        self.n_steps = n_steps
        self.pricing_date = pricing_date

    def price(self, opt: Option) -> float:
        """Pricing method for the trinomial tree.

        Args:
            opt (Option): The option associated with the trinomial tree.

        Returns:
            float: The option price.
        """
        # calculate delta t and alpha
        assert (
            self.pricing_date < opt.maturity_date
        ), "Pricing date must be before maturity date."
        self.delta_t = abs(
            ((opt.maturity_date - self.pricing_date).days / self.n_steps) / self.n_days
        )
        self.alpha = calculate_alpha(self.market.volatility, self.delta_t)
        self.discount_factor = calculate_discount_factor(
            -self.market.interest_rate, self.delta_t
        )
        self.root = Node(self.market.spot_price, self)  # S_0...
        self.__build_tree()
        return self.root.price(opt)

    def __build_tree(self) -> None:
        """build from root to leaves for each node, compute next generation if next generation is not None, compute next generation if next generation is None, stop"""
        current_mid = self.root
        for _ in range(self.n_steps):
            current_mid = self.__construct_next_generation(current_mid)

    def __construct_next_generation(self, prev_trunc_node: Node) -> Node:
        """Construct the next generation of nodes from the previous trunc node.

        Args:
        -----
            prev_trunc_node (Node): The previous trunc node.

        Returns:
        -----
            Node: The new mid (trunc) node.
        """
        self.__compute_next_nodes(prev_trunc_node)

        current_upper_neighbours = prev_trunc_node.node_up
        while current_upper_neighbours is not None:
            self.__compute_next_nodes_upward(current_upper_neighbours)
            current_upper_neighbours = current_upper_neighbours.node_up

        current_lower_neighbours = prev_trunc_node.node_down

        while current_lower_neighbours is not None:
            self.__compute_next_nodes_downward(current_lower_neighbours)
            current_lower_neighbours = current_lower_neighbours.node_down

        return prev_trunc_node.next_mid_node  # type: ignore

    def __compute_next_nodes(
        self,
        current_node: Node,
    ):
        """_summary_

        Args:
        -----
            current_node (Node): _description_
        """
        n = Node(current_node.forward_price, self)
        current_node.next_mid_node = n
        n_up = Node(current_node.up_price, self)
        current_node.next_upper_node = n_up
        current_node.next_upper_node.node_down = n
        n.node_up = n_up

        n_down = Node(current_node.down_price, self)
        current_node.next_lower_node = n_down
        current_node.next_lower_node.node_up = n
        n.node_down = n_down

    def __compute_next_nodes_upward(self, current_node: Node) -> None:
        """_summary_

        Args:
        ----
            current_node (Node): _description_
        """
        current_node.next_lower_node = current_node.node_down.next_mid_node
        current_node.next_mid_node = current_node.node_down.next_upper_node
        current_node.next_upper_node = Node(current_node.down_price, self)

        current_node.next_upper_node.node_down = current_node.next_mid_node
        current_node.next_mid_node.node_up = current_node.next_upper_node

    def __compute_next_nodes_downward(self, current_node: Node) -> None:
        """This function will iterate over the downward nodes (from the trunc) and compute the next generation of nodes successively.

        Args:
            current_node (Node): The current node, which is the downward node of the previous trunc node.
        """
        current_node.next_mid_node = current_node.node_up.next_lower_node
        current_node.next_upper_node = current_node.node_up.next_mid_node
        current_node.next_lower_node = Node(current_node.down_price, self)

        current_node.next_lower_node.node_up = current_node.next_mid_node
        current_node.next_mid_node.node_down = current_node.next_lower_node

    def __str__(self) -> str:
        return f"TrinomialTree<{self.n_steps} steps, delta_t: {self.delta_t:.3f}, alpha: {self.alpha:.3f}, root: {self.root}>"

    def __repr__(self) -> str:
        return self.__str__()
