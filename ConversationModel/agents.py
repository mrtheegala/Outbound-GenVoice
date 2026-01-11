"""
        This file is part of Outbound Phone GPT.

        Outbound Phone GPT is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        Outbound Phone GPT is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with Outbound Phone GPT.  If not, see <https://www.gnu.org/licenses/> 
"""

from __config__ import (
    BASE_GPT_TURBO_MODEL, 
    PRIOR_AUTH_CONFIG_PATH, 
    MAX_TOKENS,
    LLM_PROVIDER,
    BEDROCK_MODEL_ID
)

from copy import deepcopy
from typing import Any, Callable, Dict, List, Union

import json


from langchain.agents import AgentExecutor
from langchain.chains import RetrievalQA
from langchain.chains.base import Chain
from langchain_community.chat_models import ChatLiteLLM
from langchain_core.language_models.llms import create_base_retry_decorator
from litellm import acompletion
from pydantic import Field

from ConversationModel.chains import ConversationChain, StageAnalyzerChain
from ConversationModel.logger import time_logger
from ConversationModel.stages import (
    PRIOR_AUTH_CONVERSATION_STAGES,
    DENIAL_MANAGEMENT_CONVERSATION_STAGES,
    INSURANCE_VERIFICATION_CONVERSATION_STAGES
)
from ConversationModel.bedrock_llm import create_bedrock_llm

def _create_retry_decorator(llm: Any) -> Callable[[Any], Any]:
    import openai

    errors = [
        openai.Timeout,
        openai.APIError,
        openai.APIConnectionError,
        openai.RateLimitError,
        openai.APIStatusError,
    ]
    return create_base_retry_decorator(error_types=errors, max_retries=llm.max_retries)

class ConversationalModel(Chain):
    """Controller model for the ConversationalModel Agent."""
    conversation_history: List[str] = []
    conversation_stage_id: str = "1"
    current_conversation_stage: str = ""  # Will be set dynamically
    stage_analyzer_chain: StageAnalyzerChain = Field(...)
    sales_agent_executor: Union[AgentExecutor, None] = Field(...)
    knowledge_base: Union[RetrievalQA, None] = Field(...)
    conversation_chain: ConversationChain = Field(...)
    conversation_stage_dict: Dict = {}  # Will be set dynamically based on agent_role
    config_path : str = PRIOR_AUTH_CONFIG_PATH
    model_name  : str = BASE_GPT_TURBO_MODEL
    max_tokens : int = MAX_TOKENS
    
    config : dict = {}
    extra_fields : dict = {}
    merged_config : dict = {}
    required_fields : set = set(['prompt', 'agent_name'])
    
    def __init__(self, **data):
        """ Initialises the agent with both all fileds specified by the agent configuration JSON  """
        super().__init__(**data)
        
        # CRITICAL: Ensure conversation_stage_id is initialized BEFORE loading config
        # The config prompt template uses {conversation_stage_id} placeholder
        if not hasattr(self, 'conversation_stage_id') or self.conversation_stage_id is None:
            self.conversation_stage_id = "1"
        
        # CRITICAL: Initialize conversation_history BEFORE loading config
        if not hasattr(self, 'conversation_history') or self.conversation_history is None:
            self.conversation_history = []
        
        with open(self.config_path, "r", encoding="UTF-8") as f:
            self.config = json.load(f)
        for key, value in self.config.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra_fields[key] = value
        
        # Add conversation_stage_id to merged_config for prompt template
        # NOTE: conversation_history is NOT added here because it's dynamic and passed in _prep_messages
        self.merged_config = {
            **self.config, 
            **self.extra_fields,
            'conversation_stage_id': self.conversation_stage_id
        }
        
        recieved_data = set(self.merged_config.keys())
        missing_fields = self.required_fields - recieved_data
        if missing_fields:
            missing_fields_str = ', '.join(missing_fields)
            raise ValueError(f"Missing required fields in JSON: {missing_fields_str}")
        
        # Dynamically select conversation stages based on agent_role
        self._set_conversation_stages()
   
    def _set_conversation_stages(self):
        """
        Dynamically set conversation stages based on agent_role.
        Healthcare RCM only - supports Prior Auth, Denial Management, and Insurance Verification.
        """
        agent_role = self.config.get('agent_role', '').lower()
        
        # Determine which healthcare RCM conversation stages to use
        if 'prior authorization' in agent_role or 'prior auth' in agent_role:
            self.conversation_stage_dict = PRIOR_AUTH_CONVERSATION_STAGES
            print(f"Using PRIOR_AUTH_CONVERSATION_STAGES (10 stages)")
        elif 'denial management' in agent_role or 'denial' in agent_role:
            self.conversation_stage_dict = DENIAL_MANAGEMENT_CONVERSATION_STAGES
            print(f"Using DENIAL_MANAGEMENT_CONVERSATION_STAGES (9 stages)")
        elif 'verification' in agent_role or 'insurance verification' in agent_role or 'claims' in agent_role or 'follow-up' in agent_role:
            self.conversation_stage_dict = INSURANCE_VERIFICATION_CONVERSATION_STAGES
            print(f"Using INSURANCE_VERIFICATION_CONVERSATION_STAGES (7 stages)")
        else:
            # Default to Prior Auth if role not recognized
            self.conversation_stage_dict = PRIOR_AUTH_CONVERSATION_STAGES
            print(f"Using PRIOR_AUTH_CONVERSATION_STAGES (default, 10 stages)")
        
        # Set initial conversation stage
        self.current_conversation_stage = self.conversation_stage_dict.get("1", "")
    
    def get_attribute(self, attr_name):
        """ 
        Used to rerieve the value of any of the agent's attributes

        Args:
        attr_name : Name of the attribute as specified by the agent's configuration JSON

        Returns:
        The value of the agent's attribute
        """
        try:
            return getattr(self, attr_name)
        except AttributeError:
            if attr_name in self.extra_fields:
                return self.extra_fields[attr_name]
            else:
                return None  
        
    def retrieve_conversation_stage(self, key):
        return self.conversation_stage_dict.get(key, "1")

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    @time_logger
    def seed_agent(self):
        # Step 1: seed the conversation
        self.current_conversation_stage = self.retrieve_conversation_stage("1")
        self.conversation_history = []

    @time_logger
    def determine_conversation_stage(self):
        """ Utilises the stage analyzer chain to determine the conversation stage based on the context of the call, 
        pre-defined conversations stages and updated conversation history. This method is currenty not being used
        to minimise response latency.
        """
        self.conversation_stage_id = self.stage_analyzer_chain.run(
            conversation_history="\n".join(self.conversation_history).rstrip("\n"),
            conversation_stage_id=self.conversation_stage_id,
            conversation_stages="\n".join(
                [
                    str(key) + ": " + str(value)
                    for key, value in self.conversation_stage_dict.items()
                ]
            ),
        )

        print(f"Conversation Stage ID: {self.conversation_stage_id}")
        self.current_conversation_stage = self.retrieve_conversation_stage(
            self.conversation_stage_id
        )

        print(f"Conversation Stage: {self.current_conversation_stage}")

    def human_step(self, human_input):
        """ Processes human input by adding it to the agent's conversation history"""
        # process human input
        human_input = "User: " + human_input + " <END_OF_TURN>"
        self.conversation_history.append(human_input)

    @time_logger
    def _prep_messages(self):
        """
        Helper function to prepare messages to be passed to a streaming generator.
        """
        # Stage analyzer chain is not being used to minimise response latency
        # self.determine_conversation_stage() # Uncomment to use the stage analyzer assistant
        prompt = self.conversation_chain.prep_prompts(
            [
                dict(
                    #conversation_stage=self.current_conversation_stage, # Uncomment to use the stage analyzer assistant
                    conversation_history="\n".join(self.conversation_history),
                    **self.merged_config
                )
            ]
        )

        inception_messages = prompt[0][0].to_messages()

        message_dict = {"role": "system", "content": inception_messages[0].content}

        return [message_dict]

    async def acompletion_with_retry(self, llm: Any, **kwargs: Any) -> Any:
        """Use tenacity to retry the async completion call."""
        # Check if using BedrockClaude - use native streaming to bypass LiteLLM
        try:
            # Check if this is a BedrockClaude instance
            llm_type = llm._llm_type if hasattr(llm, '_llm_type') else None
            
            if llm_type == 'bedrock_claude' and hasattr(llm, '_astream'):
                # Use BedrockClaude's native streaming
                messages = kwargs.get('messages', [])
                stop = kwargs.get('stop', [])
                
                # Extract prompt from messages
                if messages and len(messages) > 0:
                    prompt = messages[0].get('content', '')
                else:
                    prompt = ""
                
                print(f"Using BedrockClaude native streaming with prompt length: {len(prompt)}")
                # Return async generator from BedrockClaude
                return llm._astream(prompt=prompt, stop=stop, max_tokens=kwargs.get('max_tokens', 100))
        except Exception as e:
            print(f"Error checking for BedrockClaude: {e}")
        
        # Fallback to LiteLLM for other providers
        print("Falling back to LiteLLM")
        retry_decorator = _create_retry_decorator(llm)

        @retry_decorator
        async def _completion_with_retry(**kwargs: Any) -> Any:
            return await acompletion(**kwargs)

        return await _completion_with_retry(**kwargs)

    async def _astreaming_generator(self):
        """
        Asynchronous generator to reduce I/O blocking when dealing with multiple
        clients simultaneously.

        Sometimes, the sales agent wants to take an action before the full LLM output is available.
        For instance, if we want to do text to speech on the partial LLM output.

        This function returns a streaming generator which can manipulate partial output from an LLM
        in-flight of the generation.

        Example:

        >> streaming_generator = self._astreaming_generator()
        # Now I can loop through the output in chunks:
        >> async for chunk in streaming_generator:
            await chunk ...
        Out: Chunk 1, Chunk 2, ... etc.
        See: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
        """

        messages = self._prep_messages()

        streaming_generator = await self.acompletion_with_retry(
            llm=self.conversation_chain.llm,
            messages=messages,
            stop=["<END_OF_TURN>"],  # Bedrock requires array format
            stream=True,
            model=self.model_name,
            max_tokens=self.max_tokens,
            n=1
        )

        return streaming_generator

    @classmethod
    @time_logger
    def from_llm(cls, llm: ChatLiteLLM, verbose: bool = False, **kwargs) -> "ConversationalModel":
        """Initialize the SalesGPT Controller."""
        # Pass agent_role to StageAnalyzerChain for dynamic prompt selection
        agent_role = kwargs.get('agent_role', None)
        stage_analyzer_chain = StageAnalyzerChain.from_llm(llm, verbose=verbose, agent_role=agent_role)
        prompt = deepcopy(kwargs['prompt'])
        del kwargs["prompt"]
        input_variables = list(kwargs.keys())

        conversation_chain = ConversationChain.from_llm(
                llm=llm,
                inputs = input_variables,
                verbose=verbose,
                custom_prompt=prompt,
            )
        ## Tools to be configured ##
        sales_agent_executor=None
        knowledge_base=None

        # Ensure conversation_stage_id is in kwargs if not already present
        if 'conversation_stage_id' not in kwargs:
            kwargs['conversation_stage_id'] = "1"
        
        # Remove conversation_history from kwargs if it's a string (from merged_config)
        # It will be initialized as empty list in __init__
        if 'conversation_history' in kwargs and isinstance(kwargs['conversation_history'], str):
            del kwargs['conversation_history']
        
        return cls(
            stage_analyzer_chain=stage_analyzer_chain,
            conversation_chain=conversation_chain,
            sales_agent_executor=sales_agent_executor,
            knowledge_base=knowledge_base,
            model_name=getattr(llm, 'model', None) or getattr(llm, 'model_id', 'bedrock-claude'),
            verbose=verbose,
            **kwargs,
        )
       
    def init_agent(self):
        """ Used to initialise an agent instance and seed the agent so that it's ready to take on the call"""
        
        # Choose LLM provider based on configuration
        if LLM_PROVIDER == 'bedrock':
            print(f"Initializing with AWS Bedrock model: {BEDROCK_MODEL_ID}")
            llm = create_bedrock_llm(
                model_id=BEDROCK_MODEL_ID,
                temperature=0.4,
                max_tokens=MAX_TOKENS
            )
        else:
            print(f"Initializing with OpenAI model: {self.model_name}")
            llm = ChatLiteLLM(temperature=0.4, model_name=self.model_name)

        if self.merged_config:
            self = ConversationalModel.from_llm(llm=llm, verbose=False, **self.merged_config)
        else :
            print("No agent config specified, using a standard config")

        self.seed_agent()

        return self
    

############################################### Abstract methods #################################################
    
    def _call():
        raise NotImplementedError("This method is not needed hence it hasn't been implemented")



