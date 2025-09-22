import google.generativeai as genai
import os
from typing import Dict, List

class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        # Configure Gemini API
        # Set your API key in environment variable: GEMINI_API_KEY
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Configure the API with the key
        genai.configure(api_key=api_key)
        
        # Get model name from environment variable with updated defaults
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        
        # List of known working models to try
        fallback_models = [
            'gemini-2.0-flash'
            'gemini-1.5-flash',
            'gemini-1.5-pro', 
            'gemini-1.0-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-1.0-pro'
        ]
        
        # Try to initialize with specified model first
        self.model = None
        models_to_try = [model_name] + [m for m in fallback_models if m != model_name]
        
        for model in models_to_try:
            try:
                print(f"🔄 Trying to initialize with model: {model}")
                self.model = genai.GenerativeModel(model)
                # Test the model with a simple request
                test_response = self.model.generate_content("Hello")
                print(f"✅ Successfully initialized Gemini service with model: {model}")
                break
            except Exception as e:
                print(f"❌ Failed to initialize model '{model}': {str(e)}")
                continue
        
        if self.model is None:
            # Last resort: try to list available models
            try:
                print("🔍 Listing available models...")
                available_models = genai.list_models()
                model_names = []
                for model in available_models:
                    if 'generateContent' in model.supported_generation_methods:
                        model_names.append(model.name)
                        print(f"   Available: {model.name}")
                
                if model_names:
                    # Try the first available model
                    first_model = model_names[0]
                    print(f"🔄 Trying first available model: {first_model}")
                    self.model = genai.GenerativeModel(first_model)
                    print(f"✅ Successfully initialized with: {first_model}")
                else:
                    raise Exception("No models support generateContent")
                    
            except Exception as list_error:
                print(f"❌ Failed to list models: {str(list_error)}")
                raise Exception(f"Failed to initialize any Gemini model. Please check your API key and model availability.")
    
    def analyze_rfp(self, rfp_content: str) -> str:
        """Analyze RFP content and extract requirements"""
        prompt = f"""
        You are an expert RFP analyst with deep experience in understanding and breaking down Request for Proposal documents.
        
        Please analyze the following RFP content and extract the key requirements, deliverables, and evaluation criteria.
        
        Structure your response with clear sections:
        1. Project Overview
        2. Key Requirements
        3. Technical Specifications
        4. Deliverables Expected
        5. Timeline and Milestones
        6. Evaluation Criteria
        7. Budget/Cost Considerations (if mentioned)
        
        Be thorough but concise. Focus on actionable requirements that a responding organization needs to address.
        
        RFP Content:
        {rfp_content}
        """
        
        try:
            print(f"🤖 Analyzing RFP with model: {self.model._model_name if hasattr(self.model, '_model_name') else 'unknown'}")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error in analyze_rfp: {str(e)}")
            raise Exception(f"Error analyzing RFP with Gemini: {str(e)}")
    
    def analyze_organization(self, org_content: str) -> str:
        """Analyze organization details and capabilities"""
        prompt = f"""
        Analyze the following organization document and extract key information about:
        
        1. Company Overview and Mission
        2. Core Competencies and Services
        3. Technical Capabilities
        4. Past Experience and Projects
        5. Team Expertise
        6. Certifications and Qualifications
        7. Unique Value Propositions
        
        Focus on extracting information that would be relevant for responding to RFPs.
        
        Organization Content:
        {org_content}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error analyzing organization with Gemini: {str(e)}")
    
    def create_matching_table(self, rfp_requirements: str, org_analysis: str) -> List[Dict]:
        """Create matching table between RFP requirements and organization capabilities"""
        prompt = f"""
        Based on the RFP requirements and organization analysis provided, create a comprehensive matching analysis that shows:
        - Each key RFP requirement (be thorough and extract all important requirements)
        - How the organization can address it (or if it cannot)
        - Match strength (Strong/Medium/Weak/None)
        - Any gaps or concerns
        
        Instructions:
        1. Extract ALL significant requirements from the RFP, not just a few
        2. For each requirement, assess the organization's capability to address it
        3. Use "Strong" for excellent matches, "Medium" for adequate matches, "Weak" for poor matches, "None" for missing capabilities
        4. Be thorough - include technical, operational, experience, and compliance requirements
        5. If a requirement has no corresponding organizational capability, mark it as "None"
        
        Format the response as a structured list that can be easily converted to a table.
        
        RFP Requirements:
        {rfp_requirements}
        
        Organization Analysis:
        {org_analysis}
        
        Provide the response in this exact format for each requirement:
        REQUIREMENT: [specific requirement from RFP]
        CAPABILITY: [how org can address this, or "No corresponding capability identified"]
        MATCH: [Strong/Medium/Weak/None]
        NOTES: [additional notes, gaps, or concerns]
        ---
        
        Make sure to cover at least 8-12 different requirements to provide a comprehensive analysis.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_matching_table(response.text)
        except Exception as e:
            raise Exception(f"Error creating matching table with Gemini: {str(e)}")
    
    def generate_response_prompt(self, rfp_requirements: str, org_analysis: str) -> str:
        """Generate initial prompt for RFP response"""
        prompt = f"""
        Based on the RFP requirements and organization analysis, generate a comprehensive prompt that can be used to create a winning RFP response.
        
        The prompt should guide the creation of a response that:
        1. Addresses all key RFP requirements
        2. Highlights the organization's strengths
        3. Provides specific examples and evidence
        4. Follows professional RFP response structure
        5. Demonstrates clear understanding of client needs
        
        RFP Requirements:
        {rfp_requirements}
        
        Organization Analysis:
        {org_analysis}
        
        Create a detailed prompt that will generate a complete, professional RFP response.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response prompt with Gemini: {str(e)}")
    
    def _parse_matching_table(self, response_text: str) -> List[Dict]:
        """Parse the matching table response into structured data"""
        matches = []
        entries = response_text.split('---')
        
        for entry in entries:
            if not entry.strip():
                continue
            
            lines = entry.strip().split('\n')
            match_data = {}
            
            for line in lines:
                if line.startswith('REQUIREMENT:'):
                    match_data['requirement'] = line.replace('REQUIREMENT:', '').strip()
                elif line.startswith('CAPABILITY:'):
                    match_data['capability'] = line.replace('CAPABILITY:', '').strip()
                elif line.startswith('MATCH:'):
                    match_strength = line.replace('MATCH:', '').strip().lower()
                    # Normalize match strength values
                    if match_strength in ['strong', 'excellent', 'high']:
                        match_data['match'] = 'Strong'
                    elif match_strength in ['medium', 'moderate', 'average', 'adequate']:
                        match_data['match'] = 'Medium'
                    elif match_strength in ['weak', 'low', 'poor', 'limited']:
                        match_data['match'] = 'Weak'
                    elif match_strength in ['none', 'missing', 'no', 'absent', 'not available']:
                        match_data['match'] = 'None'
                    else:
                        match_data['match'] = match_strength.title()
                elif line.startswith('NOTES:'):
                    match_data['notes'] = line.replace('NOTES:', '').strip()
            
            if match_data and 'requirement' in match_data:
                matches.append(match_data)
        
        return matches