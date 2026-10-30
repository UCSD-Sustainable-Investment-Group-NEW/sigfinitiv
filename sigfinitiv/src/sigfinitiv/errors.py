class SigfinitivError(Exception):
    """Base class for all Sigfinitiv errors."""


class ConfigError(SigfinitivError):
    """Missing or invalid configuration, such as unset credentials."""


class ContractError(SigfinitivError):
    """Data that doesn't match the agreed shape, such as a missing column."""
