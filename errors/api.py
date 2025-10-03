import config


incorrect_api_provider = ValueError(
    f"Incorrect API provider '{config.Modes.api_provider}'"
)
