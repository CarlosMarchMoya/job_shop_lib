"""Home of the `EarliestStartTimeObserver` class."""

from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_extraction import (
    FeatureObserver,
    FeatureType,
)


class EarliestStartTimeObserver(FeatureObserver):
    """Observer that adds a feature indicating the earliest start time of
    each operation, machine, and job in the graph."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
    ):
        super().__init__(dispatcher, feature_types, feature_size=1)

    def initialize_features(self):
        """Updates the features based on the current state of the
        dispatcher."""
        self._update_operation_features()
        self._update_machine_features()
        self._update_job_features()

    def _update_operation_features(self):
        """Updates the earliest start time for operation nodes."""

        for operation in self.dispatcher.unscheduled_operations():
            start_time = self.dispatcher.earliest_start_time(operation)
            adjusted_start_time = start_time - self.dispatcher.current_time()
            self.features[FeatureType.OPERATIONS][
                operation.operation_id, 0
            ] = adjusted_start_time

    def _update_machine_features(self):
        """Updates the earliest start time for machine nodes."""
        for machine_id, start_time in enumerate(
            self.dispatcher.machine_next_available_time
        ):
            self.features[FeatureType.MACHINES][machine_id, 0] = (
                start_time - self.dispatcher.current_time()
            )

    def _update_job_features(self):
        """Updates the earliest start time for job nodes."""
        for job_id, start_time in enumerate(
            self.dispatcher.job_next_available_time
        ):
            self.features[FeatureType.JOBS][job_id, 0] = (
                start_time - self.dispatcher.current_time()
            )
