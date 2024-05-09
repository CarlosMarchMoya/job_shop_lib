"""Contains factory functions for creating node feature encoders."""

from enum import Enum

from job_shop_lib.dispatching.feature_extraction import (
    IsReadyObserver,
    EarliestStartTimeObserver,
    FeatureObserver,
    DurationObserver,
    IsScheduledObserver,
    PositionInJobObserver,
    RemainingOperationsObserver,
)


class FeatureObserverType(str, Enum):
    """Enumeration of node feature creator types for the job shop scheduling
    problem."""

    IS_READY = "is_ready"
    TIME_TO_BE_READY = "time_to_be_ready"
    EARLIEST_START_TIME = "earliest_start_time"
    DURATION = "duration"
    IS_SCHEDULED = "is_scheduled"
    POSITION_IN_JOB = "position_in_job"
    REMAINING_OPERATIONS = "remaining_operations"
    COMPOSITE = "composite"


def feature_observer_factory(
    node_feature_creator_type: str | FeatureObserverType,
    **kwargs,
) -> FeatureObserver:
    """Creates and returns a node feature creator based on the specified
    node feature creator type.

    Args:
        node_feature_creator_type:
            The type of node feature creator to create.
        **kwargs:
            Additional keyword arguments to pass to the node
            feature creator constructor.

    Returns:
        A node feature creator instance.
    """
    mapping: dict[FeatureObserverType, type[FeatureObserver]] = {
        FeatureObserverType.IS_READY: IsReadyObserver,
        FeatureObserverType.TIME_TO_BE_READY: EarliestStartTimeObserver,
        FeatureObserverType.EARLIEST_START_TIME: EarliestStartTimeObserver,
        FeatureObserverType.DURATION: DurationObserver,
        FeatureObserverType.IS_SCHEDULED: IsScheduledObserver,
        FeatureObserverType.POSITION_IN_JOB: PositionInJobObserver,
        FeatureObserverType.REMAINING_OPERATIONS: RemainingOperationsObserver,
    }
    feature_creator = mapping[node_feature_creator_type]  # type: ignore[index]
    return feature_creator(**kwargs)
