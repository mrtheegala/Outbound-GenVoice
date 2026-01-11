import os
from dotenv import load_dotenv

# Load `.env` content file
load_dotenv()

# Set up the directory paths within your project
AGENT_CONFIGS_FOLDER = f'{os.getcwd()}/example_agent_configs'
AGENT_CACHE_FOLDER = f'{os.getcwd()}/example_cache_files'
AGENT_AUDIO_FOLDER = f"{os.getcwd()}/example_audio_files" 

# Configure Twilio
ACCOUNT_SID : str = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN : str = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUM : str = os.getenv('TWILIO_PHONE_NUMBER')

# Configure LLM Provider (AWS Bedrock or OpenAI)
LLM_PROVIDER : str = os.getenv('LLM_PROVIDER', 'bedrock')  # Options: 'bedrock' or 'openai'

# Configure Open AI (if using OpenAI):
OPENAI_API_KEY : str = os.getenv('OPENAI_API_KEY', '')
BASE_GPT_TURBO_MODEL : str = "gpt-3.5-turbo-0125"

# Configure AWS Bedrock (if using Bedrock):
AWS_REGION : str = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID : str = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY : str = os.getenv('AWS_SECRET_ACCESS_KEY', '')
BEDROCK_MODEL_ID : str = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')

# Common LLM settings
MAX_TOKENS : int = 100

# Configure Eleven Labs
ELEVEN_LABS_API_KEY : str = os.getenv('ELEVEN_LABS_API_KEY')
VOICE_ID : str = os.getenv('ELEVEN_LABS_VOICE_ID')
MODEL_ID : str = os.getenv('ELEVEN_LABS_TURBO_MODEL_ID')
STREAMING_LATENCY_VAL : str = '4'
ENABLE_SSML_PARSE : bool = True
VOICE_SETTINGS : dict = {"stability": 0.71, "similarity_boost": 0.5}
OUTPUT_FORMAT : str  = 'ulaw_8000'
ELEVEN_LABS_URI : str = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input?model_id={MODEL_ID}&enable_ssml_parsing={ENABLE_SSML_PARSE}&optimize_streaming_latency={STREAMING_LATENCY_VAL}&output_format={OUTPUT_FORMAT}"
END_OF_STREAM_SIGNAL = b"END"

# Configure Deepgram
DEEPGRAM_API_KEY : str = os.getenv('DEEPGRAM_API_KEY')
DEEPGRAM_MODEL : str = os.getenv("DEEPGRAM_MODEL_ID")
VERSION : str = "latest"
LANGUAGE : str = "en-US"
PUNCTUATE : str = "true"
INTERIM_RESULTS : str = "true"
ENDPOINTING : str = "true"
UTTERANCE_END_MS : str = "1000"
VAD_EVENTS : str = "true"
ENCODING : str = "mulaw"
SAMPLE_RATE: str = 8000
DEEPGRAM_URI: str = f"wss://api.deepgram.com/v1/listen?model={DEEPGRAM_MODEL}&language={LANGUAGE}&version={VERSION}&punctuate={PUNCTUATE}&interim_results={INTERIM_RESULTS}&endpointing={ENDPOINTING}&utterance_end_ms={UTTERANCE_END_MS}&sample_rate={SAMPLE_RATE}&encoding={ENCODING}&vad_events={VAD_EVENTS}"
HEADERS : dict = {'Authorization': f'Token {DEEPGRAM_API_KEY}'}
DEFAULT_MESSAGE : str = "Sorry, can you repeat that again?" # This will the default transcription output


# Configure your server using Ngrok: https://ngrok.com/docs/getting-started/
HTTP_SERVER_PORT : int = 3000 
NGROK_HTTPS_URL : str = os.getenv('NGROK_HTTPS_URL', 'https://arbitrable-bradley-unpacific.ngrok-free.dev')
WEBSOCKET_SUBDOMAIN : str = NGROK_HTTPS_URL.replace("https://", "")
BASE_WEBSOCKET_URL : str = f"wss://{WEBSOCKET_SUBDOMAIN}"

# Define session management key
SECRET_KEY : str = "secret!"

# Healthcare RCM Agent Configurations
PRIOR_AUTH_CONFIG_PATH : str = f'{AGENT_CONFIGS_FOLDER}/Prior_Auth_Agent_config.json'
PRIOR_AUTH_CACHE_PATH : str = f'{AGENT_CACHE_FOLDER}/prior_auth.pkl'
DENIAL_MGMT_CONFIG_PATH : str = f'{AGENT_CONFIGS_FOLDER}/Denial_Management_Agent_config.json'
DENIAL_MGMT_CACHE_PATH : str = f'{AGENT_CACHE_FOLDER}/denial_mgmt.pkl'
INSURANCE_VERIFY_CONFIG_PATH : str = f'{AGENT_CONFIGS_FOLDER}/Insurance_Verification_Agent_config.json'
INSURANCE_VERIFY_CACHE_PATH : str = f'{AGENT_CACHE_FOLDER}/insurance_verify.pkl'
CLAIMS_FOLLOWUP_CONFIG_PATH : str = f'{AGENT_CONFIGS_FOLDER}/Insurance_Claims_Agent.json'
CLAIMS_FOLLOWUP_CACHE_PATH : str = f'{AGENT_CACHE_FOLDER}/claims_followup.pkl'

# Agent configuration (These will configure your ConversationalModel worker)
# Change this to use different healthcare RCM agents:
# - For prior authorization: PRIOR_AUTH_CONFIG_PATH
# - For denial management: DENIAL_MGMT_CONFIG_PATH
# - For insurance verification: INSURANCE_VERIFY_CONFIG_PATH
# - For claims follow-up: CLAIMS_FOLLOWUP_CONFIG_PATH
AGENT_CACHE_FILE : str = PRIOR_AUTH_CACHE_PATH
AGENT_CONFIG_PATH : str = PRIOR_AUTH_CONFIG_PATH

# Agent type mapping for dynamic selection
AGENT_CONFIGS = {
    'prior_auth': {
        'config_path': PRIOR_AUTH_CONFIG_PATH,
        'cache_path': PRIOR_AUTH_CACHE_PATH,
        'storage_dir': 'prior_auth_records'
    },
    'denial_mgmt': {
        'config_path': DENIAL_MGMT_CONFIG_PATH,
        'cache_path': DENIAL_MGMT_CACHE_PATH,
        'storage_dir': 'denial_mgmt_records'
    },
    'insurance_verify': {
        'config_path': INSURANCE_VERIFY_CONFIG_PATH,
        'cache_path': INSURANCE_VERIFY_CACHE_PATH,
        'storage_dir': 'insurance_verify_records'
    },
    'claims_followup': {
        'config_path': CLAIMS_FOLLOWUP_CONFIG_PATH,
        'cache_path': CLAIMS_FOLLOWUP_CACHE_PATH,
        'storage_dir': 'claims_followup_records'
    }
}

def get_agent_config(agent_type: str = 'prior_auth'):
    """Get agent configuration paths by type"""
    if agent_type not in AGENT_CONFIGS:
        raise ValueError(f"Unknown agent type: {agent_type}. Valid types: {list(AGENT_CONFIGS.keys())}")
    return AGENT_CONFIGS[agent_type]


# This is a key value pair to match the output of the filler predictor model to a filler audio file to be played on the call
#          -->  'key' : output_label
#          -->  'value' : file_path
LABEL_TO_FILLER = {
    'General-Inquiry' : f"{AGENT_AUDIO_FOLDER}/General-Inquiry-filler.wav",
    'Company-Inquiry' : f"{AGENT_AUDIO_FOLDER}/Company-Inquiry-filler.wav",
    'Concern' : f"{AGENT_AUDIO_FOLDER}/Concern-filler.wav",
    'Confused' : f"{AGENT_AUDIO_FOLDER}/Confused-filler.wav",
    'Positive-Intent' : f"{AGENT_AUDIO_FOLDER}/Positive-Intent-filler.wav",
    'Dont-Understand' : f"{AGENT_AUDIO_FOLDER}/Dont-Understand-filler.wav",
    'None' : None
}