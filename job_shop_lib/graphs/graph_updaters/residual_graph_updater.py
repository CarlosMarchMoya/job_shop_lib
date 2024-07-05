"""Home of the `ResidualGraphUpdater` class."""

from job_shop_lib import ScheduledOperation, UninitializedAttributeError
from job_shop_lib.graphs import NodeType, JobShopGraph
from job_shop_lib.graphs.graph_updaters import (
    GraphUpdater,
    remove_completed_operations,
)
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    IsCompletedObserver,
    FeatureType,
)
from job_shop_lib.dispatching import create_or_get_observer, DispatcherObserver


class ResidualGraphUpdater(GraphUpdater):
    """Updates the residual graph based on the completed operations."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        job_shop_graph: JobShopGraph,
        is_singleton: bool = False,
        subscribe: bool = True,
        remove_completed_machine_nodes: bool = True,
        remove_completed_job_nodes: bool = True,
    ):
        """Initializes the residual graph updater.

        Args:
            dispatcher:
                The dispatcher instance to observe.
            job_shop_graph:
                The job shop graph to update.
            is_singleton:
                If True, ensures only one instance of this observer type is
                subscribed to the dispatcher. Defaults to False.
            subscribe:
                If True, automatically subscribes the observer to the
                dispatcher. Defaults to True.
            remove_completed_machine_nodes:
                If True, removes completed machine nodes from the graph.
                Defaults to True.
            remove_completed_job_nodes:
                If True, removes completed job nodes from the graph.
                Defaults to True.
        """

        self._is_completed_observer: None | IsCompletedObserver = None
        self.remove_completed_job_nodes = remove_completed_job_nodes
        self.remove_completed_machine_nodes = remove_completed_machine_nodes
        self._initialize_is_completed_observer_attribute(dispatcher)

        # It is important to initialize the `IsCompletedObserver` before
        # calling the parent class constructor to ensure the observer is
        # updated before the `update` method of this class is called.
        super().__init__(
            dispatcher,
            job_shop_graph,
            is_singleton=is_singleton,
            subscribe=subscribe,
        )

        self.remove_completed_machine_nodes = remove_completed_machine_nodes
        self.remove_completed_job_nodes = remove_completed_job_nodes

    def _initialize_is_completed_observer_attribute(
        self, dispatcher: Dispatcher
    ):
        def has_all_features(observer: DispatcherObserver) -> bool:
            if not isinstance(observer, IsCompletedObserver):
                return False  # Make the type checker happy.

            for feature_type in feature_types:
                if feature_type not in observer.features.keys():
                    return False
            return True

        feature_types: list[FeatureType] = []
        if self.remove_completed_machine_nodes:
            feature_types.append(FeatureType.MACHINES)
        if self.remove_completed_job_nodes:
            feature_types.append(FeatureType.JOBS)
        if feature_types:
            self._is_completed_observer = create_or_get_observer(
                dispatcher,
                IsCompletedObserver,
                condition=has_all_features,
                feature_types=feature_types,
                is_singleton=False,
            )

    @property
    def is_completed_observer(self) -> IsCompletedObserver:
        """Returns the `IsCompletedObserver` instance."""
        if self._is_completed_observer is None:
            raise UninitializedAttributeError(
                "The `is_completed_observer` attribute has not been "
                "initialized. Set `remove_completed_machine_nodes` or "
                "remove_completed_job_nodes` to True when initializing the "
                "ResidualGraphUpdater."
            )
        return self._is_completed_observer

    def update(self, scheduled_operation: ScheduledOperation) -> None:
        """Updates the residual graph based on the completed operations."""
        remove_completed_operations(
            self.job_shop_graph,
            completed_operations=self.dispatcher.completed_operations(),
        )
        graph_has_machine_nodes = bool(
            self.job_shop_graph.nodes_by_type[NodeType.MACHINE]
        )
        if self.remove_completed_machine_nodes and graph_has_machine_nodes:
            self._remove_completed_machine_nodes()

        graph_has_machine_nodes = bool(
            self.job_shop_graph.nodes_by_type[NodeType.JOB]
        )
        if self.remove_completed_job_nodes and graph_has_machine_nodes:
            self._remove_completed_job_nodes()

    def _remove_completed_machine_nodes(self):
        """Removes the completed machine nodes from the graph if they are
        not already removed."""

        for machine_id, is_completed in enumerate(
            self.is_completed_observer.features[FeatureType.MACHINES].flatten()
        ):
            if is_completed == 1 and not self.job_shop_graph.is_removed(
                machine_node := self.job_shop_graph.get_machine_node(
                    machine_id
                )
            ):
                self.job_shop_graph.remove_node(machine_node.node_id)

    def _remove_completed_job_nodes(self):
        """Removes the completed job nodes from the graph if they are not
        already removed."""

        for job_id, is_completed in enumerate(
            self.is_completed_observer.features[FeatureType.JOBS]
        ):
            if is_completed == 1 and not self.job_shop_graph.is_removed(
                job_node := self.job_shop_graph.get_job_node(job_id)
            ):
                self.job_shop_graph.remove_node(job_node.node_id)
