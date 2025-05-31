# Copilot Custom Instructions

These instructions ensure high-quality, maintainable, and consistent code for Home Assistant custom components in this repository.

## General Coding Standards

- Use Python 3.10+ syntax, type hints, and best practices for all code suggestions.
- If unsure about a Home Assistant feature or API, ask for clarification before proceeding.
- Always check the latest Home Assistant documentation for APIs and features before implementing.
- Always reference all files in the repository when providing code suggestions or thinking about implementation.

## Home Assistant API Usage

- Use Home Assistant's `hass` object for accessing the Home Assistant core and services.
- Use Home Assistant's `config` object for accessing configuration data.
- Use Home Assistant's `async_setup_entry` and `async_unload_entry` for setting up and unloading integrations.
- Use Home Assistant's `async_add_entities` for adding entities to the Home Assistant state machine.
- Use Home Assistant's `async_setup` and `async_setup_platform` for setting up platforms.
- Use Home Assistant's `async_add_job` for scheduling jobs.
- Use Home Assistant's `async_track_time_interval` for scheduling periodic tasks.
- Use Home Assistant's `async_dispatcher_connect` for connecting to signals.
- Use Home Assistant's `async_create_task` for creating async tasks.
- Use Home Assistant's `async_get_clientsession` for making HTTP requests.
- Use Home Assistant's `async_get_hass` for accessing the Home Assistant instance.
- Use Home Assistant's `async_get_config_entry` for accessing configuration entries.
- Use Home Assistant's `async_get_entity_registry` for accessing the entity registry.
- Use Home Assistant's `async_get_device_registry` for accessing the device registry.
- Use Home Assistant's `async_get_storage` for accessing storage.
- Use Home Assistant's `async_get_event_loop` for accessing the event loop.

## File Structure & Documentation

- Follow Home Assistant’s official development guidelines and file structure conventions:
  - Place custom components in `custom_components/your_component/`.
  - Place tests in the `tests/` directory, using pytest and Home Assistant test utilities.
  - Place developer reference docs in `dev-docs/home-assistant/` and user docs in `README.md` or `docs/`.

## Linting & Formatting

- Use Ruff and Black for linting and formatting. Run them before submitting code.

## Documentation & Comments

- Prefer clear, concise docstrings and comments in code (in English).
- Use Google-style or Home Assistant-style docstrings.

## Dependency Management

- Avoid unnecessary dependencies unless explicitly requested.
- Use built-in or Home Assistant utilities when possible.

## Code Quality

- Write modular, testable, and async-friendly code.
- Use type hints for all functions and classes.

## Testing

- When suggesting tests:
  - Use pytest and Home Assistant test utilities.
  - Place test files in the `tests/` directory, mirroring the structure of the component.
  - Include tests for config flows, options flows, and entity behavior where applicable.

## Commit Messages

- Generate commit messages that are clear and descriptive, following the conventional commits format. Give them to me in Markdown format.
- Use the following commit message format:
  - `feat: <description>` for new features
  - `fix: <description>` for bug fixes
  - `docs: <description>` for documentation changes
  - `style: <description>` for style changes (formatting, etc.)
  - `refactor: <description>` for code refactoring
  - `test: <description>` for adding or updating tests
  - `chore: <description>` for maintenance tasks
- Example commit message:

  ```
  feat: add async config flow for torque integration

  - Implemented async config flow using Home Assistant best practices.
  - Added tests for config flow and options flow.
  ```
