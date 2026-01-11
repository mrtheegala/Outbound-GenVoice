"""
AWS Bedrock LLM Integration for Outbound Phone GPT

This module provides a wrapper for AWS Bedrock Claude models to work with
the existing Langchain-based conversation system.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, AsyncIterator
import boto3
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from pydantic import Field

from __config__ import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BEDROCK_MODEL_ID, MAX_TOKENS


class BedrockClaude(LLM):
    """
    AWS Bedrock Claude LLM wrapper compatible with Langchain.
    
    This class provides both synchronous and asynchronous methods for
    interacting with Claude models via AWS Bedrock.
    """
    
    model_id: str = BEDROCK_MODEL_ID
    region_name: str = AWS_REGION
    max_tokens: int = MAX_TOKENS
    temperature: float = 0.7
    streaming: bool = True
    max_retries: int = 3  # Add retry support for compatibility
    
    bedrock_client: Any = Field(default=None, exclude=True)
    bedrock_runtime: Any = Field(default=None, exclude=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize boto3 clients
        session_kwargs = {
            'region_name': self.region_name
        }
        
        # Add credentials if provided
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            session_kwargs['aws_access_key_id'] = AWS_ACCESS_KEY_ID
            session_kwargs['aws_secret_access_key'] = AWS_SECRET_ACCESS_KEY
        
        session = boto3.Session(**session_kwargs)
        self.bedrock_client = session.client('bedrock')
        self.bedrock_runtime = session.client('bedrock-runtime')
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM type."""
        return "bedrock_claude"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Synchronous call to Bedrock Claude.
        
        Args:
            prompt: The input prompt
            stop: Optional list of stop sequences
            run_manager: Optional callback manager
            
        Returns:
            The generated text response
        """
        # Prepare request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            "temperature": kwargs.get('temperature', self.temperature),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if stop:
            request_body["stop_sequences"] = stop
        
        try:
            # Invoke the model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                return ""
                
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return ""
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Asynchronous call to Bedrock Claude.
        
        Args:
            prompt: The input prompt
            stop: Optional list of stop sequences
            run_manager: Optional callback manager
            
        Returns:
            The generated text response
        """
        # Run synchronous call in executor for async compatibility
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._call,
            prompt,
            stop,
            None,
            **kwargs
        )
    
    async def _astream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Asynchronous streaming call to Bedrock Claude.
        
        Args:
            prompt: The input prompt
            stop: Optional list of stop sequences
            run_manager: Optional callback manager
            
        Yields:
            Text chunks as they are generated
        """
        # Prepare request body for streaming
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            "temperature": kwargs.get('temperature', self.temperature),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if stop:
            request_body["stop_sequences"] = stop
        
        try:
            # Invoke model with streaming
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Stream the response
            stream = response.get('body')
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        chunk_obj = json.loads(chunk.get('bytes').decode())
                        
                        # Handle different event types
                        if chunk_obj['type'] == 'content_block_delta':
                            if 'delta' in chunk_obj and 'text' in chunk_obj['delta']:
                                text = chunk_obj['delta']['text']
                                if run_manager:
                                    await run_manager.on_llm_new_token(text)
                                yield text
                                
        except Exception as e:
            print(f"Error streaming from Bedrock: {e}")
            yield ""
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return identifying parameters for this LLM."""
        return {
            "model_id": self.model_id,
            "region_name": self.region_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


def create_bedrock_llm(
    model_id: str = BEDROCK_MODEL_ID,
    temperature: float = 0.7,
    max_tokens: int = MAX_TOKENS,
    streaming: bool = True
) -> BedrockClaude:
    """
    Factory function to create a BedrockClaude LLM instance.
    
    Args:
        model_id: The Bedrock model ID to use
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
        streaming: Whether to enable streaming responses
        
    Returns:
        Configured BedrockClaude instance
    """
    return BedrockClaude(
        model_id=model_id,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming
    )
