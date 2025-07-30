# Changelog

All remarkable changes for this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) 
and this project adheres to [SemVer](https://semver.org).

---
## [1.1.0] - 2025-07-xx

### Added
- Now you can define a personalized prompt for the agent.

---
## [1.0.0] - 2025-07-27

### Added
- Support to multiple entry, referenced as `Account`.
- Support to multiple agents.
- Each agent now has:
  - Tokens count sensors according to the [stackspot response](https://ai.stackspot.com/docs/agents/agent-api/agents-api#api-example).
  - An entity `conversation`.
- The entry also receives a global tokens count sensor on their own.
- The agent now has a parameter to control the message number to keep in the section history.
  - This can be configured either in creation or editing.
- When configuring a `Assistant` now accepts all the languages supported by ha.
- Translation files for `en` and `pt-br`

---
## [0.0.1] - 2025-07-09

### Added
- First working version of the integration, implementing basic support for communication with the StackSpot AI agent.