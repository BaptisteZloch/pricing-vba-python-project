from datetime import datetime, timedelta
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Literal, Optional, Tuple

from tqdm import tqdm
from pricing_library.node import Node
from pricing_library.market import Market
from pricing_library.option import Option
from pricing_library.utils import (
    calculate_alpha,
    calculate_discount_factor,
    measure_time,
)


class TrinomialTree:
    n_days = 365

    def __init__(
        self,
        market: Market,
        pricing_date: datetime,
        n_steps: int,
    ) -> None:
        """Constructor of the TrinomialTree class.

        Args:
        ----
            market (Market): The Market object containing market informations.
            pricing_date (datetime): Pricing date of the option, could be today but must be before maturity_date.
            n_steps (int): The number of steps in the trinomial tree.
        """
        self.market = market
        self.n_steps = n_steps
        self.pricing_date = pricing_date

    @measure_time
    def price(self, opt: Option, draw_tree: bool = False) -> float:
        """Option pricing method for the trinomial tree.

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
        # calculate alpha and discount factor
        self.alpha = calculate_alpha(self.market.volatility, self.delta_t)
        self.discount_factor = calculate_discount_factor(
            self.market.interest_rate, self.delta_t
        )
        self.__build_tree()  # first we need to build the tree before pricing
        price = self.root.price(opt)  # price the option
        if draw_tree:
            self.__plot_tree()
        return price

    @measure_time
    def __build_tree(self) -> None:
        """build from root to leaves for each node, compute next generation if next generation is not None, compute next generation if next generation is None, stop"""
        self.root = Node(self.market.spot_price, self, self.pricing_date)
        current_mid = self.root
        current_date = self.pricing_date
        # iterate over the number of steps to construct the nodes generation
        for _ in tqdm(
            range(self.n_steps),
            total=self.n_steps,
            desc="Building tree...",
            leave=False,
        ):
            current_date = current_date + timedelta(days=self.delta_t * self.n_days)
            current_mid = self.__construct_next_generation(current_mid, current_date)

    def __construct_next_generation(
        self, prev_trunc_node: Node, date_time: Optional[datetime] = None
    ) -> Node:
        """Construct the next generation of nodes from the previous trunc node.

        Args:
        -----
            prev_trunc_node (Node): The previous trunc node.
            date_time (Optional[datetime], optional): The date associated with the current generation it depends on delta t and starting date. Defaults to None.

        Returns:
        -----
            Node: The new mid (trunc) node.
        """
        # first compute the next mid generation
        self.__compute_next_nodes(prev_trunc_node, date_time)

        # then construct the next upper generations until the node has no upper node
        current_upper_neighbours = prev_trunc_node.node_up
        while current_upper_neighbours is not None:
            self.__compute_next_nodes_upward(current_upper_neighbours, date_time)
            current_upper_neighbours = current_upper_neighbours.node_up

        current_lower_neighbours = prev_trunc_node.node_down
        # then construct the next lower generations until the node has no lower node
        while current_lower_neighbours is not None:
            self.__compute_next_nodes_downward(current_lower_neighbours, date_time)
            current_lower_neighbours = current_lower_neighbours.node_down

        return prev_trunc_node.next_mid_node

    def __compute_next_nodes(
        self, current_node: Node, date_time: Optional[datetime] = None
    ) -> None:
        """Compute the next generation of nodes from the current node at a given date.

        Args:
        -----
            current_node (Node): The current node.
            date_time (Optional[datetime], optional): The date associated with the current generation it depends on delta t and starting date. Defaults to None.
        """
        n = Node(
            current_node.forward_price, self, date_time
        )  # create the next mid node
        current_node.next_mid_node = n  # link the current node to the next mid node
        n_up = Node(
            current_node.up_price, self, date_time
        )  # create the next upper node
        current_node.next_upper_node = (
            n_up  # link the current node to the next upper node
        )
        current_node.next_upper_node.node_down = (
            n  # link the next upper node to the next mid node
        )
        n.node_up = n_up  # link the next mid node to the next upper node

        n_down = Node(
            current_node.down_price, self, date_time
        )  # create the next lower node
        current_node.next_lower_node = (
            n_down  # link the current node to the next lower node
        )
        current_node.next_lower_node.node_up = (
            n  # link the next lower node to the next mid node
        )
        n.node_down = n_down  # link the next mid node to the next lower node

    def __compute_next_nodes_upward(
        self, current_node: Node, date_time: Optional[datetime] = None
    ) -> None:
        """Compute and link the next generation of nodes upward from the current node.

        Args:
        ----
            current_node (Node): _description_
            date_time (Optional[datetime], optional): The date associated with the current generation it depends on delta t and starting date. Defaults to None.
        """
        current_node.next_lower_node = current_node.node_down.next_mid_node
        current_node.next_mid_node = current_node.node_down.next_upper_node
        current_node.next_upper_node = Node(current_node.up_price, self, date_time)

        current_node.next_upper_node.node_down = current_node.next_mid_node
        current_node.next_mid_node.node_up = current_node.next_upper_node

    def __compute_next_nodes_downward(
        self, current_node: Node, date_time: Optional[datetime] = None
    ) -> None:
        """This function will iterate over the downward nodes (from the trunc) and compute the next generation of nodes successively.

        Args:
            current_node (Node): The current node, which is the downward node of the previous trunc node.
        """
        current_node.next_mid_node = current_node.node_up.next_lower_node
        current_node.next_upper_node = current_node.node_up.next_mid_node
        current_node.next_lower_node = Node(current_node.down_price, self, date_time)

        current_node.next_lower_node.node_up = current_node.next_mid_node
        current_node.next_mid_node.node_down = current_node.next_lower_node

    @measure_time
    def __plot_tree(
        self, label_to_plot: Literal["spot_price", "option_price"] = "spot_price"
    ) -> None:
        """Display the tree using networkx library. If the number of steps is greater than 20, the tree will be unreadable. This is a breadth-first tree traversal algorithm.

        Args:
            label_to_plot (Literal[&quot;spot_price&quot;, &quot;option_price&quot;], optional): _description_. Defaults to "option_price".
        """

        if self.n_steps < 20:
            G = nx.Graph()
            nodes: List[Tuple[Node, Optional[Node], int]] = [
                (self.root, None, 0)
            ]  # stack containing (current, parent, depth)

            while nodes:
                current, parent, depth = nodes.pop()
                G.add_node(current, pos=(current.spot_price, -depth))
                if parent is not None:
                    G.add_edge(parent, current)
                if current.next_upper_node:
                    nodes.append((current.next_upper_node, current, depth + 1))
                if current.next_mid_node:
                    nodes.append((current.next_mid_node, current, depth + 1))
                if current.next_lower_node:
                    nodes.append((current.next_lower_node, current, depth + 1))

            pos = nx.get_node_attributes(G, "pos")
            labels = {
                node: f"{datetime.strftime(node.time_step, '%Y-%m-%d')}\n{eval('node.'+label_to_plot):.2f}"
                for node in G.nodes()
            }

            nx.draw(
                G,
                pos,
                labels=labels,
                with_labels=True,
                node_size=500,
                node_color="lightblue",
                font_size=8,
                font_color="black",
            )
            plt.title("Arbre trinomial d'options")
            plt.axis("off")
            plt.show()
        else:
            print(
                f"Tree is too big to be displayed. Number of steps: {self.n_steps} > 20"
            )

    def __str__(self) -> str:
        return f"TrinomialTree<{self.n_steps} steps, delta_t: {self.delta_t:.3f}, alpha: {self.alpha:.3f}, root: {self.root}>"

    def __repr__(self) -> str:
        return self.__str__()
