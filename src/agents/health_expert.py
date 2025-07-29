"""
Health Domain Expert Agent for txtIntelligentReader

This agent specializes in medical terminology expertise and health domain content scoring.
"""

from crewai import Agent
import medspacy
from typing import List, Dict, Any, Optional


class HealthDomainExpertAgent:
    """
    Agent specialized in medical terminology and health domain content.
    
    Role: Senior Medical Editor
    Goal: Score medical relevance and identify health domain content
    Backstory: You are a medical professional with 15+ years editing medical texts 
               for international organizations.
    """
    
    def __init__(self, llm):
        """Initialize the Health Domain Expert Agent with LLM and medical NLP."""
        self.agent = Agent(
            role="Senior Medical Editor",
            goal="Score medical relevance and identify health domain content",
            backstory="You are a medical professional with 15+ years editing medical texts for international organizations.",
            llm=llm,
            verbose=True
        )
        self.nlp = medspacy.load()
        self.health_terms = self._load_health_terms()
    
    def score_health_relevance(self, sentence: str) -> float:
        """
        Score medical relevance of a sentence.
        
        Args:
            sentence: Sentence to analyze for health relevance
            
        Returns:
            Health relevance score between 0.0 and 1.0
        """
        score_factors = []
        
        # Factor 1: Medical terminology density
        term_score = self._calculate_medical_term_score(sentence)
        score_factors.append(term_score)
        
        # Factor 2: Medical entities from medspaCy
        entity_score = self._calculate_medical_entity_score(sentence)
        score_factors.append(entity_score)
        
        # Factor 3: Health domain patterns
        pattern_score = self._calculate_health_pattern_score(sentence)
        score_factors.append(pattern_score)
        
        # Factor 4: Medical context indicators
        context_score = self._calculate_medical_context_score(sentence)
        score_factors.append(context_score)
        
        # Weighted average with emphasis on entities and terminology
        weights = [0.3, 0.4, 0.2, 0.1]  # term, entity, pattern, context
        weighted_score = sum(score * weight for score, weight in zip(score_factors, weights))
        
        return min(weighted_score, 1.0)
    
    def identify_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify medical entities in text using medspaCy.
        
        Args:
            text: Text to analyze for medical entities
            
        Returns:
            List of identified medical entities with metadata
        """
        try:
            # Process text with medspaCy pipeline
            doc = self.nlp(text)
            
            entities = []
            for ent in doc.ents:
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': getattr(ent, 'confidence', 0.8),  # Default confidence
                    'description': self._get_entity_description(ent.label_)
                }
                entities.append(entity_info)
            
            return entities
            
        except Exception as e:
            # Fallback to manual entity detection if medspaCy fails
            return self._manual_entity_detection(text)
    
    def validate_medical_terminology(self, text: str) -> Dict[str, Any]:
        """
        Validate medical terminology usage and accuracy.
        
        Args:
            text: Text containing medical terminology
            
        Returns:
            Validation results with accuracy metrics
        """
        validation_results = {
            'valid_terms': [],
            'invalid_terms': [],
            'suggested_corrections': [],
            'terminology_accuracy': 0.0,
            'domain_specificity': 0.0
        }
        
        # Extract potential medical terms
        potential_terms = self._extract_potential_medical_terms(text)
        
        for term in potential_terms:
            if self._is_valid_medical_term(term):
                validation_results['valid_terms'].append(term)
            else:
                validation_results['invalid_terms'].append(term)
                suggestion = self._suggest_term_correction(term)
                if suggestion:
                    validation_results['suggested_corrections'].append({
                        'original': term,
                        'suggested': suggestion
                    })
        
        # Calculate accuracy metrics
        total_terms = len(potential_terms)
        if total_terms > 0:
            validation_results['terminology_accuracy'] = len(validation_results['valid_terms']) / total_terms
        
        validation_results['domain_specificity'] = self._calculate_domain_specificity(text)
        
        return validation_results
    
    def get_health_domain_confidence(self, sentence: str, entities: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score for health domain classification.
        
        Args:
            sentence: Sentence to analyze
            entities: Previously identified medical entities
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence_factors = []
        
        # Entity-based confidence
        entity_confidence = self._calculate_entity_confidence(entities)
        confidence_factors.append(entity_confidence)
        
        # Terminology-based confidence
        term_confidence = self._calculate_terminology_confidence(sentence)
        confidence_factors.append(term_confidence)
        
        # Context-based confidence
        context_confidence = self._calculate_context_confidence(sentence)
        confidence_factors.append(context_confidence)
        
        # Structure-based confidence (medical text patterns)
        structure_confidence = self._calculate_medical_structure_confidence(sentence)
        confidence_factors.append(structure_confidence)
        
        # Return weighted average
        return sum(confidence_factors) / len(confidence_factors)
    
    def _calculate_medical_term_score(self, text: str) -> float:
        """
        Calculate score based on medical terminology density.
        
        Args:
            text: Text to analyze
            
        Returns:
            Medical term score between 0.0 and 1.0
        """
        words = text.lower().split()
        if not words:
            return 0.0
        
        medical_word_count = 0
        for word in words:
            # Remove punctuation for matching
            clean_word = word.strip('.,!?;:()[]{}"\'')
            if clean_word in [term.lower() for term in self.health_terms]:
                medical_word_count += 1
        
        # Calculate density
        density = medical_word_count / len(words)
        
        # Convert to score (cap at reasonable density)
        return min(density * 3, 1.0)  # 33% density = max score
    
    def _calculate_medical_entity_score(self, text: str) -> float:
        """
        Calculate score based on identified medical entities.
        
        Args:
            text: Text to analyze
            
        Returns:
            Medical entity score between 0.0 and 1.0
        """
        entities = self.identify_medical_entities(text)
        
        if not entities:
            return 0.0
        
        # Score based on number and confidence of entities
        entity_score = 0.0
        for entity in entities:
            confidence = entity.get('confidence', 0.5)
            entity_score += confidence
        
        # Normalize by text length (entities per 100 characters)
        text_length = len(text)
        if text_length > 0:
            normalized_score = (entity_score / text_length) * 100
            return min(normalized_score, 1.0)
        
        return 0.0
    
    def _calculate_health_pattern_score(self, text: str) -> float:
        """
        Calculate score based on health domain patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Health pattern score between 0.0 and 1.0
        """
        import re
        
        text_lower = text.lower()
        score = 0.0
        
        # Medical measurement patterns
        if re.search(r'\d+\s*(mg|ml|cc|units?|doses?|tablets?)', text_lower):
            score += 0.3
        
        # Medical procedure patterns
        if re.search(r'(perform|conduct|undergo|receive)\s+(surgery|treatment|therapy|examination)', text_lower):
            score += 0.3
        
        # Diagnostic patterns
        if re.search(r'(diagnos|symptom|condition|disorder|disease)', text_lower):
            score += 0.2
        
        # Treatment patterns
        if re.search(r'(treat|medic|therap|prescrib|administer)', text_lower):
            score += 0.2
        
        # Medical professional patterns
        if re.search(r'(doctor|physician|nurse|specialist|clinician)', text_lower):
            score += 0.1
        
        # Healthcare facility patterns
        if re.search(r'(hospital|clinic|medical center|healthcare)', text_lower):
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_medical_context_score(self, text: str) -> float:
        """
        Calculate score based on medical context indicators.
        
        Args:
            text: Text to analyze
            
        Returns:
            Medical context score between 0.0 and 1.0
        """
        text_lower = text.lower()
        score = 0.0
        
        # Clinical context indicators
        clinical_indicators = [
            'clinical', 'medical', 'healthcare', 'therapeutic',
            'diagnostic', 'treatment', 'patient care', 'health'
        ]
        
        for indicator in clinical_indicators:
            if indicator in text_lower:
                score += 0.1
        
        # Medical documentation patterns
        if any(phrase in text_lower for phrase in ['medical record', 'case study', 'clinical trial']):
            score += 0.2
        
        # Professional medical language
        if any(phrase in text_lower for phrase in ['according to', 'studies show', 'research indicates']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_entity_description(self, label: str) -> str:
        """
        Get description for medical entity label.
        
        Args:
            label: Entity label from medspaCy
            
        Returns:
            Human-readable description
        """
        descriptions = {
            'PERSON': 'Person name',
            'ORG': 'Organization',
            'GPE': 'Geopolitical entity',
            'CONDITION': 'Medical condition',
            'TREATMENT': 'Medical treatment',
            'MEDICATION': 'Medication or drug',
            'ANATOMY': 'Anatomical structure',
            'SYMPTOM': 'Medical symptom',
            'PROCEDURE': 'Medical procedure',
            'DEVICE': 'Medical device'
        }
        return descriptions.get(label, f'Medical entity ({label})')
    
    def _manual_entity_detection(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback manual entity detection when medspaCy fails.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of manually detected entities
        """
        entities = []
        text_lower = text.lower()
        
        # Simple pattern-based detection
        medical_patterns = {
            'medication': ['antibiotic', 'painkiller', 'medication', 'drug', 'pill', 'tablet'],
            'condition': ['infection', 'disease', 'disorder', 'syndrome', 'condition'],
            'procedure': ['surgery', 'operation', 'procedure', 'treatment', 'therapy'],
            'anatomy': ['heart', 'lung', 'brain', 'liver', 'kidney', 'bone', 'muscle']
        }
        
        for category, terms in medical_patterns.items():
            for term in terms:
                if term in text_lower:
                    start_pos = text_lower.find(term)
                    entities.append({
                        'text': term,
                        'label': category.upper(),
                        'start': start_pos,
                        'end': start_pos + len(term),
                        'confidence': 0.6,  # Lower confidence for manual detection
                        'description': f'Manual detection: {category}'
                    })
        
        return entities
    
    def _extract_potential_medical_terms(self, text: str) -> List[str]:
        """
        Extract potential medical terms from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of potential medical terms
        """
        import re
        
        # Extract words that might be medical terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter for potential medical terms (longer words, specific patterns)
        potential_terms = []
        for word in words:
            # Medical terms often have specific patterns
            if (len(word) >= 4 and 
                (word.endswith(('itis', 'osis', 'emia', 'ology', 'therapy', 'gram')) or
                 word.startswith(('anti', 'pre', 'post', 'hyper', 'hypo')) or
                 word in self.health_terms)):
                potential_terms.append(word)
        
        return list(set(potential_terms))  # Remove duplicates
    
    def _is_valid_medical_term(self, term: str) -> bool:
        """
        Check if a term is a valid medical term.
        
        Args:
            term: Term to validate
            
        Returns:
            True if valid medical term
        """
        return term.lower() in [t.lower() for t in self.health_terms]
    
    def _suggest_term_correction(self, term: str) -> Optional[str]:
        """
        Suggest correction for invalid medical term.
        
        Args:
            term: Invalid term
            
        Returns:
            Suggested correction or None
        """
        # Simple similarity-based suggestion
        term_lower = term.lower()
        
        for valid_term in self.health_terms:
            valid_lower = valid_term.lower()
            # Simple similarity check (could be improved with edit distance)
            if (abs(len(term_lower) - len(valid_lower)) <= 2 and
                term_lower[:3] == valid_lower[:3]):
                return valid_term
        
        return None
    
    def _calculate_domain_specificity(self, text: str) -> float:
        """
        Calculate how specific the text is to health domain.
        
        Args:
            text: Text to analyze
            
        Returns:
            Domain specificity score between 0.0 and 1.0
        """
        # Count highly specific medical terms
        specific_terms = [
            'pathology', 'etiology', 'prognosis', 'differential diagnosis',
            'contraindication', 'pharmacokinetics', 'therapeutic index',
            'bioavailability', 'epidemiology', 'nosocomial'
        ]
        
        text_lower = text.lower()
        specific_count = sum(1 for term in specific_terms if term in text_lower)
        
        # Normalize by text length
        words = text.split()
        if len(words) > 0:
            return min(specific_count / len(words) * 10, 1.0)
        
        return 0.0
    
    def _calculate_entity_confidence(self, entities: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence based on identified entities.
        
        Args:
            entities: List of identified entities
            
        Returns:
            Entity-based confidence score
        """
        if not entities:
            return 0.0
        
        # Average confidence of all entities
        total_confidence = sum(entity.get('confidence', 0.5) for entity in entities)
        return total_confidence / len(entities)
    
    def _calculate_terminology_confidence(self, text: str) -> float:
        """
        Calculate confidence based on medical terminology.
        
        Args:
            text: Text to analyze
            
        Returns:
            Terminology-based confidence score
        """
        return self._calculate_medical_term_score(text)
    
    def _calculate_context_confidence(self, text: str) -> float:
        """
        Calculate confidence based on medical context.
        
        Args:
            text: Text to analyze
            
        Returns:
            Context-based confidence score
        """
        return self._calculate_medical_context_score(text)
    
    def _calculate_medical_structure_confidence(self, text: str) -> float:
        """
        Calculate confidence based on medical text structure.
        
        Args:
            text: Text to analyze
            
        Returns:
            Structure-based confidence score
        """
        import re
        
        text_lower = text.lower()
        score = 0.0
        
        # Medical documentation structure patterns
        if re.search(r'(chief complaint|history of present illness|physical examination)', text_lower):
            score += 0.4
        
        # Clinical measurement patterns
        if re.search(r'\d+\s*(bpm|mmhg|celsius|fahrenheit|mg/dl)', text_lower):
            score += 0.3
        
        # Medical abbreviation patterns
        if re.search(r'\b(bp|hr|temp|wbc|rbc|ecg|mri|ct)\b', text_lower):
            score += 0.2
        
        # Professional medical language structure
        if re.search(r'(patient presents with|diagnosis of|treatment plan)', text_lower):
            score += 0.3
        
        return min(score, 1.0)
    
    def _load_health_terms(self) -> List[str]:
        """
        Load comprehensive health terms database.
        
        Returns:
            List of 200+ medical terms and concepts
        """
        return [
            "patient", "treatment", "diagnosis", "symptoms", "therapy",
            "medication", "clinical", "hospital", "doctor", "nurse",
            "disease", "infection", "surgery", "medical", "health",
            "care", "healthcare", "medicine", "pharmaceutical", "drug",
            "vaccine", "immunization", "prevention", "screening", "test",
            "laboratory", "radiology", "pathology", "anatomy", "physiology",
            "epidemiology", "public health", "surveillance", "outbreak",
            "pandemic", "epidemic", "virus", "bacteria", "pathogen",
            "antibiotic", "antiviral", "therapeutic", "intervention",
            "protocol", "guideline", "standard", "practice", "procedure",
            "examination", "assessment", "evaluation", "monitoring",
            "follow-up", "referral", "consultation", "specialist",
            "primary care", "secondary care", "tertiary care", "emergency",
            "urgent", "acute", "chronic", "condition", "disorder",
            "syndrome", "complication", "adverse", "side effect",
            "contraindication", "indication", "dosage", "administration",
            "injection", "oral", "topical", "intravenous", "intramuscular",
            "subcutaneous", "inhaled", "nebulizer", "oxygen", "ventilator",
            "intensive care", "ICU", "ward", "clinic", "outpatient",
            "inpatient", "admission", "discharge", "recovery", "rehabilitation",
            "physical therapy", "occupational therapy", "mental health",
            "psychiatry", "psychology", "counseling", "therapy session",
            "behavioral", "cognitive", "emotional", "social", "spiritual",
            "palliative", "hospice", "end-of-life", "terminal", "prognosis",
            "mortality", "morbidity", "survival", "quality of life",
            "functional status", "disability", "impairment", "limitation",
            "mobility", "independence", "activities of daily living",
            "nutrition", "diet", "dietary", "malnutrition", "obesity",
            "underweight", "BMI", "weight", "height", "growth", "development",
            "pediatric", "geriatric", "maternal", "pregnancy", "prenatal",
            "postnatal", "delivery", "birth", "newborn", "infant", "child",
            "adolescent", "adult", "elderly", "aging", "senior", "caregiver",
            "family", "community", "population", "demographic", "risk factor",
            "protective factor", "determinant", "outcome", "indicator",
            "metric", "measurement", "data", "statistics", "research",
            "study", "trial", "evidence", "systematic review", "meta-analysis",
            "guideline", "recommendation", "best practice", "standard of care",
            "quality improvement", "patient safety", "adverse event",
            "medical error", "incident", "reporting", "investigation",
            "root cause", "corrective action", "prevention", "mitigation",
            "risk management", "quality assurance", "accreditation",
            "certification", "licensing", "regulation", "compliance",
            "ethics", "informed consent", "confidentiality", "privacy",
            "HIPAA", "medical record", "documentation", "coding", "billing",
            "reimbursement", "insurance", "coverage", "access", "equity",
            "disparity", "barrier", "challenge", "solution", "innovation",
            "technology", "telemedicine", "digital health", "electronic health record",
            "EHR", "EMR", "health information", "interoperability", "integration",
            "workflow", "process", "system", "infrastructure", "capacity",
            "resource", "staffing", "training", "education", "competency",
            "skill", "knowledge", "expertise", "specialization", "certification",
            "continuing education", "professional development", "leadership",
            "management", "administration", "governance", "policy", "strategy",
            "planning", "implementation", "evaluation", "monitoring", "assessment",
            "improvement", "sustainability", "scalability", "replication",
            "adaptation", "customization", "localization", "cultural competency",
            "language", "translation", "interpretation", "communication",
            "health literacy", "patient education", "health promotion",
            "disease prevention", "wellness", "fitness", "exercise", "activity",
            "lifestyle", "behavior", "habit", "change", "modification",
            "intervention", "program", "service", "delivery", "provision",
            "coordination", "collaboration", "partnership", "network",
            "alliance", "coalition", "stakeholder", "engagement", "participation",
            "involvement", "empowerment", "advocacy", "support", "assistance"
        ]
