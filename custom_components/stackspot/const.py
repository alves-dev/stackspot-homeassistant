from homeassistant.helpers import llm

INTEGRATION_NAME = 'StackSpot AI'
DOMAIN = 'stackspot'
MANAGER = 'key-manager'

# CONF
CONF_ACCOUNT = 'account_name'
CONF_ACCOUNT_DEFAULT = 'My account'
CONF_REALM = 'realm'
CONF_REALM_DEFAULT = 'stackspot-freemium'
CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_KEY = 'client_key'

# CONF AGENT
CONF_AGENT_NAME = 'agent_name'
CONF_AGENT_NAME_DEFAULT = 'Agent'
CONF_AGENT_ID = 'agent_id'
CONF_AGENT_MAX_MESSAGES_HISTORY = "max_messages_history"
CONF_AGENT_PROMPT = 'agent_prompt'
CONF_AGENT_PROMPT_DEFAULT = (
        llm.BASE_PROMPT
        + '\n'
        + llm.DEFAULT_INSTRUCTIONS_PROMPT
        + '\n'
          '{## The variable {{user}} is provided by integration ##}'
          '\n'
          'My name is {{ user }}'
)

# CONF AI TASK
CONF_AI_TASK_NAME = 'agent_name'
CONF_AI_TASK_NAME_DEFAULT = 'StackSpot AI task'
CONF_AI_TASK_AGENT_ID = 'agent_id'
CONF_AI_TASK_PROMPT = 'agent_prompt'
CONF_AI_TASK_PROMPT_DEFAULT = (
        llm.BASE_PROMPT
        + '\n'
        + llm.DEFAULT_INSTRUCTIONS_PROMPT
)

# CONF KS
CONF_KS_NAME = 'ks_name'
CONF_KS_NAME_DEFAULT = 'HA: Entities'
CONF_KS_SLUG = 'ks_slug'
CONF_KS_TEMPLATE = 'ks_template'
CONF_KS_TEMPLATE_DEFAULT = (
    '{## The variable {{exposed_entities}} is provided by integration ##}'
    '\n'
    'Exposed entities and their aliases: {{ exposed_entities }}'
)
CONF_KS_INTERVAL_UPDATE = 'interval_update'
CONF_KS_INTERVAL_UPDATE_DEFAULT = {'days': 0, 'hours': 48, 'minutes': 0, 'seconds': 0}

# CONF OPTIONS
# CONF_HA_ENTITIES_ACCESS = "ha_entities_access"
# CONF_TOKEN_RESET_INTERVAL = "token_reset_interval"

# CONF_TOKEN_RESET_INTERVAL Options
TOKEN_RESET_INTERVAL_DAY = "day"
TOKEN_RESET_INTERVAL_MONTH = "month"
TOKEN_RESET_INTERVAL_NEVER = "never"

# SENSORS
SENSOR_TOTAL_GENERAL_TOKEN = 'general_total_tokens'
SENSOR_TOTAL_TOKEN = 'total_tokens'
SENSOR_USER_TOKEN = 'user_tokens'
SENSOR_ENRICHMENT_TOKEN = 'enrichment_tokens'
SENSOR_OUTPUT_TOKEN = 'output_tokens'
SENSOR_KS_LAST_UPDATE = 'ks_last_update'

# AGENTS
AGENTS_KEY = 'agents'

# CONTEXT
SECONDS_KEEP_CONVERSATION_HISTORY = 3600

SELECT_RESET_INTERVAL_ENTITY = "token_reset_interval_select"

# TYPES SUBENTRY
SUBENTRY_AGENT = 'agent'
SUBENTRY_AI_TASK = 'ai_task'
SUBENTRY_KS = 'knowledge_source'

# Template Key
TEMPLATE_KEY_USER = 'user'
TEMPLATE_KEY_EXPOSED_ENTITIES = 'exposed_entities'
