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
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
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
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
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
        Based on the RFP requirements and organization analysis provided, create a matching table that shows:
        - Each key RFP requirement
        - How the organization can address it
        - Match strength (Strong/Medium/Weak)
        - Any gaps or concerns
        
        Format the response as a structured list that can be easily converted to a table.
        
        RFP Requirements:
        {rfp_requirements}
        
        Organization Analysis:
        {org_analysis}
        
        Provide the response in this exact format:
        REQUIREMENT: [requirement]
        CAPABILITY: [how org can address]
        MATCH: [Strong/Medium/Weak]
        NOTES: [additional notes]
        ---
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
                    match_data['match'] = line.replace('MATCH:', '').strip()
                elif line.startswith('NOTES:'):
                    match_data['notes'] = line.replace('NOTES:', '').strip()
            
            if match_data:
                matches.append(match_data)
        
        return matches
