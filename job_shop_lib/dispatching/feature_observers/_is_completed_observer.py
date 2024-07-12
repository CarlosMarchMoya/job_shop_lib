"""Home of the `IsCompletedObserver` class."""

from typing import Iterable

import numpy as np

from job_shop_lib import ScheduledOperation
from job_shop_lib.dispatching import Dispatcher
from job_shop_lib.dispatching.feature_observers import (
    FeatureObserver,
    FeatureType,
    RemainingOperationsObserver,
)


class IsCompletedObserver(FeatureObserver):
    """Observer that adds a binary feature indicating whether each operation,
    machine, or job has been completed."""

    def __init__(
        self,
        dispatcher: Dispatcher,
        feature_types: list[FeatureType] | FeatureType | None = None,
        subscribe: bool = True,
    ):
        feature_types = self._get_feature_types_list(feature_types)
        self.remaining_ops_per_machine = np.zeros(
            (dispatcher.instance.num_machines, 1), dtype=int
        )
        self.remaining_ops_per_job = np.zeros(
            (dispatcher.instance.num_jobs, 1), dtype=int
        )
        super().__init__(
            dispatcher,
            feature_types=feature_types,
            subscribe=subscribe,
        )

    def initialize_features(self):
        remaining_ops_observer = self._get_remaining_operations_observer(
            self.dispatcher, self.features
        )
        if remaining_ops_observer is not None:
            if FeatureType.JOBS in self.features:
                self.remaining_ops_per_job = remaining_ops_observer.features[
                    FeatureType.JOBS
                ].copy()
            if FeatureType.MACHINES in self.features:
                self.remaining_ops_per_machine = (
                    remaining_ops_observer.features[
                        FeatureType.MACHINES
                    ].copy()
                )
            return

        # If there is no remaining operations observer, we need to
        # compute the remaining operations ourselves.
        # We iterate over all operations using scheduled_operations
        # instead of uncompleted_operations, because in this case
        # they will output the same operations, and the former is slightly
        # more efficient.

        # First, we se everything to 0.
        self.remaining_ops_per_machine[:, 0] = 0
        self.remaining_ops_per_job[:, 0] = 0
        for operation in self.dispatcher.unscheduled_operations():
            if FeatureType.JOBS in self.features:
                self.remaining_ops_per_job[operation.job_id, 0] += 1
            if FeatureType.MACHINES in self.features:
                self.remaining_ops_per_machine[operation.machines, 0] += 1

    def update(self, scheduled_operation: ScheduledOperation):
        if FeatureType.OPERATIONS in self.features:
            completed_operations = [
                op.operation_id
                for op in self.dispatcher.completed_operations()
            ]
            self.features[FeatureType.OPERATIONS][completed_operations, 0] = 1
        if FeatureType.MACHINES in self.features:
            self.remaining_ops_per_machine[
                scheduled_operation.operation.machines, 0
            ] -= 1
            is_completed = (
                self.remaining_ops_per_machine[
                    scheduled_operation.operation.machines, 0
                ]
                == 0
            )
            self.features[FeatureType.MACHINES][
                scheduled_operation.operation.machines, 0
            ] = is_completed
        if FeatureType.JOBS in self.features:
            job_id = scheduled_operation.job_id
            self.remaining_ops_per_job[job_id, 0] -= 1
            is_completed = self.remaining_ops_per_job[job_id, 0] == 0
            self.features[FeatureType.JOBS][job_id, 0] = is_completed

    def _get_remaining_operations_observer(
        self, dispatcher: Dispatcher, feature_types: Iterable[FeatureType]
    ) -> RemainingOperationsObserver | None:
        for observer in dispatcher.subscribers:
            if not isinstance(observer, RemainingOperationsObserver):
                continue
            has_same_features = all(
                feature_type in observer.features
                for feature_type in feature_types
            )
            if has_same_features:
                return observer
        return None
