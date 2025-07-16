INTEGRATION_NAME = 'StackSpot AI'
DOMAIN = 'stackspot'

# CONF
CONF_AGENT_NAME= 'agent_name'
CONF_AGENT_ID= 'agent'
CONF_REALM = 'realm'
CONF_CLIENT_ID = 'client_id'
CONF_CLIENT_KEY = 'client_key'

CONF_AGENT_NAME_DEFAULT= 'Agent'
CONF_REALM_DEFAULT = 'stackspot-freemium'

# CONF OPTIONS
CONF_MAX_MESSAGES_HISTORY = "max_messages_history"
CONF_HA_ENTITIES_ACCESS = "ha_entities_access"
CONF_TOKEN_RESET_INTERVAL = "token_reset_interval"

# CONF_TOKEN_RESET_INTERVAL Options
TOKEN_RESET_INTERVAL_DAY = "day"
TOKEN_RESET_INTERVAL_MONTH = "month"
TOKEN_RESET_INTERVAL_NEVER = "never"

# SENSORS
SENSOR_TOKENS_KEY = 'stackspot_token_sensors'
SENSOR_TOTAL_TOKEN= 'total_tokens'
SENSOR_USER_TOKEN = 'user_tokens'
SENSOR_ENRICHMENT_TOKEN = 'enrichment_tokens'
SENSOR_OUTPUT_TOKEN = 'output_tokens'

SENSOR_TOTAL_GENERAL_TOKEN= 'general_total_tokens'

# AGENTS
AGENTS_KEY = 'agents'

# CONTEXT
SECONDS_KEEP_CONVERSATION_HISTORY=3600