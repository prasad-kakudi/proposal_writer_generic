import google.generativeai as genai
import os
from typing import Dict, List

class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Get model name from environment variable with updated defaults
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        
        # List of known working models to try (FIXED: Added missing comma)
        fallback_models = [
            'gemini-2.0-flash',  # Fixed missing comma
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
        """Analyze RFP content and extract requirements with enhanced structure"""
        prompt = f"""
        You are an expert RFP analyst with deep experience in understanding and breaking down Request for Proposal documents across various industries and project types.
        
        Please analyze the following RFP content and extract the key requirements, deliverables, and evaluation criteria in a well-structured format.
        
        Structure your response with these clear sections:
        
        **1. PROJECT OVERVIEW**
        - Brief summary of the project scope and objectives
        - Target timeline and key milestones
        - Budget range (if mentioned)
        
        **2. MANDATORY REQUIREMENTS**
        - Technical specifications that must be met
        - Compliance and certification requirements
        - Minimum experience or qualification thresholds
        
        **3. DELIVERABLES EXPECTED**
        - Specific outputs, products, or services required
        - Documentation and reporting requirements
        - Implementation and support expectations
        
        **4. EVALUATION CRITERIA**
        - How proposals will be scored and weighted
        - Key decision factors and priorities
        - Submission requirements and deadlines
        
        **5. TECHNICAL SPECIFICATIONS**
        - Detailed technical requirements
        - Integration needs and constraints
        - Performance and scalability expectations
        
        **6. ORGANIZATIONAL REQUIREMENTS**
        - Team composition and expertise needed
        - Past experience demonstrations required
        - References and case studies expected
        
        Be thorough but concise. Focus on actionable requirements that a responding organization needs to address. Use bullet points for clarity within each section.
        
        RFP Content:
        {rfp_content}
        """
        
        try:
            print(f"🤖 Analyzing RFP with enhanced structure...")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error in analyze_rfp: {str(e)}")
            raise Exception(f"Error analyzing RFP with Gemini: {str(e)}")
    
    def analyze_organization(self, org_content: str) -> str:
        """Analyze organization details and capabilities with enhanced focus"""
        prompt = f"""
        You are an expert business analyst specializing in organizational capability assessment for competitive proposal responses.
        
        Analyze the following organization document and extract key information in these structured categories:
        
        **1. COMPANY PROFILE**
        - Company size, structure, and years in business
        - Mission, vision, and core values
        - Market position and competitive advantages
        
        **2. CORE COMPETENCIES & SERVICES**
        - Primary business areas and specializations
        - Service offerings and product portfolio
        - Unique methodologies or approaches
        
        **3. TECHNICAL CAPABILITIES**
        - Technology platforms and tools expertise
        - Development methodologies and frameworks
        - Infrastructure and technical resources
        
        **4. EXPERIENCE & TRACK RECORD**
        - Relevant past projects and client engagements
        - Industry-specific experience
        - Project scale and complexity handled
        
        **5. TEAM EXPERTISE**
        - Key personnel qualifications and experience
        - Team structure and roles
        - Professional certifications and credentials
        
        **6. CERTIFICATIONS & QUALIFICATIONS**
        - Industry certifications and standards compliance
        - Quality management systems
        - Security clearances and compliance frameworks
        
        **7. DIFFERENTIATORS & VALUE PROPOSITIONS**
        - What sets this organization apart from competitors
        - Innovation capabilities and thought leadership
        - Client success stories and testimonials
        
        Focus on extracting information that would be directly relevant for crafting compelling RFP responses.
        
        Organization Content:
        {org_content}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error analyzing organization with Gemini: {str(e)}")
    
    def create_matching_table(self, rfp_requirements: str, org_analysis: str) -> List[Dict]:
        """Create comprehensive matching table with enhanced analysis"""
        prompt = f"""
        As an expert proposal strategist, create a comprehensive matching analysis between the RFP requirements and organization capabilities.
        
        IMPORTANT INSTRUCTIONS:
        1. Extract ALL significant requirements from the RFP - aim for 10-15 distinct requirements
        2. For each requirement, provide a detailed assessment of organizational fit
        3. Use precise match strength ratings: Strong/Medium/Weak/None
        4. Include strategic recommendations for addressing gaps
        5. Prioritize requirements by criticality to RFP success
        
        MATCH STRENGTH DEFINITIONS:
        - **Strong**: Organization has proven track record and excellent capabilities
        - **Medium**: Organization has relevant experience but may need some enhancement
        - **Weak**: Organization has limited relevant experience or capabilities
        - **None**: No corresponding organizational capability identified
        
        For each requirement, provide:
        - Clear requirement statement from RFP
        - Specific organizational capability or experience that addresses it
        - Match strength with brief justification
        - Strategic notes on how to strengthen the response
        
        Format each entry exactly as:
        REQUIREMENT: [specific requirement from RFP]
        CAPABILITY: [detailed organizational capability or "No corresponding capability identified"]
        MATCH: [Strong/Medium/Weak/None]
        NOTES: [strategic recommendations, gap analysis, or enhancement suggestions]
        ---
        
        Ensure comprehensive coverage of technical, operational, experience, compliance, and delivery requirements.
        
        RFP Requirements:
        {rfp_requirements}
        
        Organization Analysis:
        {org_analysis}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_matching_table(response.text)
        except Exception as e:
            raise Exception(f"Error creating matching table with Gemini: {str(e)}")
    
    def generate_response_prompt(self, rfp_requirements: str, org_analysis: str) -> str:
        """Generate comprehensive prompt for winning RFP response"""
        prompt = f"""
        As an expert proposal writer with extensive experience in creating winning RFP responses, generate a comprehensive prompt that will produce a professional, compelling, and complete RFP response.
        
        The prompt should guide the creation of a response that:
        
        **STRATEGIC ELEMENTS:**
        - Demonstrates clear understanding of client needs and challenges
        - Positions the organization as the ideal partner
        - Addresses all mandatory requirements comprehensively
        - Highlights unique value propositions and differentiators
        
        **STRUCTURAL REQUIREMENTS:**
        - Follows professional RFP response format and best practices
        - Includes executive summary, technical approach, and implementation plan
        - Provides specific examples, case studies, and quantifiable benefits
        - Addresses evaluation criteria with targeted responses
        
        **CONTENT GUIDELINES:**
        - Use persuasive but professional tone
        - Include specific methodologies and frameworks
        - Provide detailed project timeline and milestones
        - Address risk mitigation and quality assurance
        - Include team qualifications and organizational credentials
        
        Create a detailed prompt that will generate a complete, professional RFP response document that maximizes the chances of winning the contract.
        
        The prompt should be comprehensive enough to produce a response of 2000-4000 words covering all critical aspects.
        
        RFP Requirements:
        {rfp_requirements}
        
        Organization Analysis:
        {org_analysis}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response prompt with Gemini: {str(e)}")
    
    def _parse_matching_table(self, response_text: str) -> List[Dict]:
        """Parse the matching table response into structured data with validation"""
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
            
            # Validate that we have minimum required fields
            if match_data and 'requirement' in match_data and 'match' in match_data:
                # Set defaults for missing fields
                if 'capability' not in match_data:
                    match_data['capability'] = 'Capability assessment pending'
                if 'notes' not in match_data:
                    match_data['notes'] = 'No additional notes'
                matches.append(match_data)
        
        return matches