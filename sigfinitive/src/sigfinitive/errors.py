class SigfinitiveError(Exception):
    """Base class for all Sigfinitive errors."""


class ConfigError(SigfinitiveError):
    """Missing or invalid configuration, such as unset credentials."""


class ContractError(SigfinitiveError):
    """Data that doesn't match the agreed shape, such as a missing column."""
