# Changelog

All remarkable changes for this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) 
and this project adheres to [SemVer](https://semver.org).

---
## [1.3.0] - 2025-09-xx

### Added
- New variable `exposed_entities` for prompts

---
## [1.2.2] - 2025-08-25

### Fix
- Injects username into prompt, only when context has this information

---
## [1.2.1] - 2025-08-14

### Fix
- Token validation correction when expired

---
## [1.2.0] - 2025-08-12

### Added
- Added AI task support:
  - You can now create a new input to generate data with an agent.
  - See: https://www.home-assistant.io/integrations/ai_task
  - **Note:** Requires Home Assistant in version `2025.8.0`

---
## [1.1.0] - 2025-08-01

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