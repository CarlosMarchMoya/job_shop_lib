"""Home of the `FeatureObserver` class and `FeatureType` enum."""

import enum

import numpy as np

from job_shop_lib import ScheduledOperation
from job_shop_lib.exceptions import ValidationError
from job_shop_lib.dispatching import Dispatcher, DispatcherObserver


class FeatureType(str, enum.Enum):
    """Types of features that can be extracted."""

    OPERATIONS = "operations"
    MACHINES = "machines"
    JOBS = "jobs"


class FeatureObserver(DispatcherObserver):
    """Base class for feature observers.

    Feature observers are not singleton by default. This means that more than
    one instance of the same feature observer type can be subscribed to the
    dispatcher. This is useful when the first subscriber only observes a subset
    of the features, and the second subscriber observes a different subset of
    them. For example, the first subscriber could observe only the
    operation-related features, while the second subscriber could observe the
    jobs.
    """

    _is_singleton = False
    _feature_size: dict[FeatureType, int] | int = 1
    _supported_feature_types = list(FeatureType)

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        subscribe: bool = True,
        feature_types: list[FeatureType] | FeatureType | None = None,
    ):
        feature_types = self._get_feature_types_list(feature_types)
        if isinstance(self._feature_size, int):
            feature_size = {
                feature_type: self._feature_size
                for feature_type in feature_types
            }
        super().__init__(dispatcher, subscribe=subscribe)

        number_of_entities = {
            FeatureType.OPERATIONS: dispatcher.instance.num_operations,
            FeatureType.MACHINES: dispatcher.instance.num_machines,
            FeatureType.JOBS: dispatcher.instance.num_jobs,
        }
        self.feature_dimensions = {
            feature_type: (
                number_of_entities[feature_type],
                feature_size[feature_type],
            )
            for feature_type in feature_types
        }
        self.features = {
            feature_type: np.zeros(
                self.feature_dimensions[feature_type],
                dtype=np.float32,
            )
            for feature_type in feature_types
        }
        self.initialize_features()

    @property
    def feature_size(self) -> dict[FeatureType, int]:
        """Returns the size of the features."""
        if isinstance(self._feature_size, int):
            return {
                feature_type: self._feature_size
                for feature_type in self.features
            }
        return self._feature_size

    @property
    def supported_feature_types(self) -> list[FeatureType]:
        """Returns the supported feature types."""
        return self._supported_feature_types

    def initialize_features(self):
        """Initializes the features based on the current state of the
        dispatcher."""

    def update(self, scheduled_operation: ScheduledOperation):
        """Updates the features based on the scheduled operation.

        By default, this method just calls :meth:`initialize_features`.

        Args:
            ScheduledOperation:
                The operation that has been scheduled.
        """
        self.initialize_features()

    def reset(self):
        """Sets features to zero and calls to :meth:``initialize_features``."""
        self.set_features_to_zero()
        self.initialize_features()

    def set_features_to_zero(
        self, exclude: FeatureType | list[FeatureType] | None = None
    ):
        """Sets features to zero."""
        if exclude is None:
            exclude = []
        if isinstance(exclude, FeatureType):
            exclude = [exclude]

        for feature_type in self.features:
            if feature_type in exclude:
                continue
            self.features[feature_type][:] = 0.0

    def _get_feature_types_list(
        self,
        feature_types: list[FeatureType] | FeatureType | None,
    ) -> list[FeatureType]:
        """Returns a list of feature types.

        Args:
            feature_types:
                A list of feature types or a single feature type. If ``None``,
                all feature types are returned.
        """
        if isinstance(feature_types, FeatureType):
            return [feature_types]
        if feature_types is None:
            return self._supported_feature_types

        for feature_type in feature_types:
            if feature_type not in self._supported_feature_types:
                raise ValidationError(
                    f"Feature type {feature_type} is not supported."
                )
        return feature_types

    def __str__(self):
        out = [self.__class__.__name__, ":\n"]
        out.append("-" * len(out[0]))
        for feature_type, feature in self.features.items():
            out.append(f"\n{feature_type.value}:\n{feature}")
        return "".join(out)
