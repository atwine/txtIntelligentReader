#!/usr/bin/env python3
"""
Health Context Filter (Layer 2) for txtIntelligentReader

This filter identifies medical/health terminology and domain relevance.
"""

import re
from typing import List, Dict, Any, Set, Tuple
from pathlib import Path


class HealthContextFilter:
    """
    Second layer filter that identifies medical/health terminology and domain relevance.
    
    This filter handles:
    - Medical terminology detection
    - Health domain relevance scoring
    - Medical entity recognition
    - Domain context analysis
    - Health-specific pattern matching
    """
    
    def __init__(self, health_threshold: float = 0.3):
        """
        Initialize the HealthContextFilter with medical terminology database.
        
        Args:
            health_threshold: Minimum health relevance score to keep sentences
        """
        self.health_threshold = health_threshold
        self.medical_terms = self._load_medical_terms()
        self.medical_patterns = self._compile_medical_patterns()
        self.anatomy_terms = self._load_anatomy_terms()
        self.condition_terms = self._load_condition_terms()
        self.treatment_terms = self._load_treatment_terms()
        self.medication_patterns = self._compile_medication_patterns()
        
        # Statistics tracking
        self.stats = {
            'total_processed': 0,
            'health_relevant': 0,
            'medical_entities_found': 0,
            'high_relevance': 0,
            'medium_relevance': 0,
            'low_relevance': 0
        }
    
    def filter_by_health_context(self, sentences: List[str], threshold: float = None) -> List[str]:
        """
        Filter sentences based on health domain relevance.
        
        Args:
            sentences: List of sentences to filter
            threshold: Override default health threshold
            
        Returns:
            Filtered list of health-relevant sentences
        """
        if not sentences:
            return []
        
        threshold = threshold or self.health_threshold
        filtered = []
        self.stats['total_processed'] = len(sentences)
        
        for sentence in sentences:
            if sentence and isinstance(sentence, str):
                relevance_score = self.score_health_relevance(sentence)
                if relevance_score >= threshold:
                    filtered.append(sentence)
                    self.stats['health_relevant'] += 1
                    
                    # Categorize relevance level
                    if relevance_score >= 0.8:
                        self.stats['high_relevance'] += 1
                    elif relevance_score >= 0.5:
                        self.stats['medium_relevance'] += 1
                    else:
                        self.stats['low_relevance'] += 1
        
        return filtered
    
    def score_health_relevance(self, sentence: str) -> float:
        """
        Calculate health domain relevance score for a sentence.
        
        Args:
            sentence: Sentence to score
            
        Returns:
            Health relevance score between 0.0 and 1.0
        """
        if not sentence or not sentence.strip():
            return 0.0
        
        sentence_lower = sentence.lower()
        words = sentence_lower.split()
        
        # Factor 1: Medical terminology density (40% weight)
        medical_term_score = self._calculate_medical_term_score(sentence_lower, words)
        
        # Factor 2: Medical entities detection (30% weight)
        entity_score = self._calculate_entity_score(sentence_lower)
        
        # Factor 3: Health patterns matching (20% weight)
        pattern_score = self._calculate_pattern_score(sentence_lower)
        
        # Factor 4: Medical context indicators (10% weight)
        context_score = self._calculate_context_score(sentence_lower)
        
        # Weighted final score
        final_score = (
            medical_term_score * 0.4 +
            entity_score * 0.3 +
            pattern_score * 0.2 +
            context_score * 0.1
        )
        
        return min(final_score, 1.0)
    
    def _load_medical_terms(self) -> Set[str]:
        """
        Load comprehensive medical terminology database.
        
        Returns:
            Set of medical terms in lowercase
        """
        # Core medical terms database
        medical_terms = {
            # Basic medical terms
            'patient', 'doctor', 'physician', 'nurse', 'hospital', 'clinic', 'medical',
            'health', 'healthcare', 'medicine', 'treatment', 'therapy', 'diagnosis',
            'symptom', 'disease', 'condition', 'illness', 'infection', 'syndrome',
            
            # Body systems and anatomy
            'heart', 'lung', 'brain', 'liver', 'kidney', 'stomach', 'blood', 'bone',
            'muscle', 'nerve', 'skin', 'eye', 'ear', 'nose', 'throat', 'chest',
            'abdomen', 'spine', 'joint', 'tissue', 'organ', 'cell', 'artery', 'vein',
            
            # Common medical procedures
            'surgery', 'operation', 'examination', 'test', 'scan', 'biopsy', 'injection',
            'vaccination', 'immunization', 'procedure', 'consultation', 'checkup',
            'screening', 'monitoring', 'assessment', 'evaluation', 'analysis',
            
            # Medical specialties
            'cardiology', 'neurology', 'oncology', 'pediatrics', 'psychiatry',
            'dermatology', 'orthopedics', 'radiology', 'pathology', 'anesthesia',
            'emergency', 'intensive', 'surgical', 'clinical', 'therapeutic',
            
            # Common conditions
            'diabetes', 'hypertension', 'cancer', 'pneumonia', 'asthma', 'arthritis',
            'depression', 'anxiety', 'migraine', 'fracture', 'stroke', 'seizure',
            'allergy', 'inflammation', 'tumor', 'cyst', 'lesion', 'wound',
            
            # Medications and treatments
            'antibiotic', 'medication', 'drug', 'prescription', 'dose', 'dosage',
            'tablet', 'capsule', 'injection', 'infusion', 'chemotherapy', 'radiation',
            'physiotherapy', 'rehabilitation', 'recovery', 'healing',
            
            # Medical measurements and values
            'temperature', 'pressure', 'pulse', 'heartrate', 'glucose', 'cholesterol',
            'hemoglobin', 'platelet', 'white', 'red', 'count', 'level', 'normal',
            'abnormal', 'elevated', 'decreased', 'positive', 'negative',
            
            # Healthcare settings
            'ward', 'unit', 'department', 'laboratory', 'pharmacy', 'radiology',
            'pathology', 'morgue', 'ambulance', 'emergency', 'outpatient', 'inpatient'
        }
        
        return medical_terms
    
    def _load_anatomy_terms(self) -> Set[str]:
        """Load anatomical terms."""
        return {
            'head', 'neck', 'shoulder', 'arm', 'elbow', 'wrist', 'hand', 'finger',
            'chest', 'breast', 'back', 'spine', 'hip', 'leg', 'knee', 'ankle', 'foot',
            'toe', 'skull', 'rib', 'pelvis', 'femur', 'tibia', 'fibula', 'radius',
            'ulna', 'humerus', 'scapula', 'clavicle', 'sternum', 'vertebra'
        }
    
    def _load_condition_terms(self) -> Set[str]:
        """Load medical condition terms."""
        return {
            'acute', 'chronic', 'severe', 'mild', 'moderate', 'critical', 'stable',
            'unstable', 'progressive', 'degenerative', 'malignant', 'benign',
            'infectious', 'contagious', 'hereditary', 'genetic', 'autoimmune',
            'inflammatory', 'allergic', 'toxic', 'metabolic', 'neurological'
        }
    
    def _load_treatment_terms(self) -> Set[str]:
        """Load treatment and procedure terms."""
        return {
            'treatment', 'therapy', 'intervention', 'procedure', 'surgery', 'operation',
            'transplant', 'implant', 'bypass', 'repair', 'reconstruction', 'removal',
            'excision', 'biopsy', 'catheter', 'stent', 'pacemaker', 'dialysis',
            'transfusion', 'ventilator', 'oxygen', 'IV', 'intravenous'
        }
    
    def _compile_medical_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for medical context detection.
        
        Returns:
            List of compiled medical patterns
        """
        patterns = [
            # Medical measurements
            r'\d+\s*(mg|ml|cc|units?|doses?)',
            r'\d+/\d+\s*(mmHg|blood pressure)',
            r'\d+\s*(bpm|beats per minute)',
            r'\d+\.\d+\s*(temperature|temp)',
            
            # Medical codes and references
            r'ICD-?\d+',
            r'CPT\s*\d+',
            r'DRG\s*\d+',
            
            # Medical abbreviations
            r'\b(BP|HR|RR|O2|CO2|CBC|BUN|CT|MRI|EKG|ECG|EEG|ICU|ER|OR)\b',
            
            # Dosage patterns
            r'\d+\s*times?\s*(daily|per day|a day)',
            r'every\s+\d+\s+hours?',
            r'twice\s+(daily|a day)',
            r'once\s+(daily|a day)',
            
            # Medical time references
            r'post-?operative',
            r'pre-?operative',
            r'follow-?up',
            r'discharge',
            r'admission',
            
            # Symptom descriptions
            r'pain\s+(in|at|on)',
            r'difficulty\s+(breathing|swallowing)',
            r'shortness\s+of\s+breath',
            r'chest\s+pain',
            r'abdominal\s+pain',
            
            # Medical procedures
            r'underwent\s+\w+',
            r'performed\s+\w+',
            r'administered\s+\w+',
            r'prescribed\s+\w+',
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_medication_patterns(self) -> List[re.Pattern]:
        """Compile patterns for medication detection."""
        patterns = [
            r'\w+cillin\b',  # Antibiotics ending in -cillin
            r'\w+mycin\b',   # Antibiotics ending in -mycin
            r'\w+pril\b',    # ACE inhibitors
            r'\w+sartan\b',  # ARBs
            r'\w+statin\b',  # Statins
            r'\w+zole\b',    # Proton pump inhibitors
            r'\w+pam\b',     # Benzodiazepines
            r'\w+ine\b',     # Various medications
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _calculate_medical_term_score(self, sentence_lower: str, words: List[str]) -> float:
        """Calculate score based on medical terminology density."""
        if not words:
            return 0.0
        
        medical_word_count = 0
        for word in words:
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.medical_terms:
                medical_word_count += 1
            elif clean_word in self.anatomy_terms:
                medical_word_count += 1
            elif clean_word in self.condition_terms:
                medical_word_count += 1
            elif clean_word in self.treatment_terms:
                medical_word_count += 1
        
        if medical_word_count > 0:
            self.stats['medical_entities_found'] += medical_word_count
        
        # Calculate density with bonus for multiple terms
        density = medical_word_count / len(words)
        if medical_word_count >= 3:
            density *= 1.5  # Bonus for multiple medical terms
        
        return min(density, 1.0)
    
    def _calculate_entity_score(self, sentence_lower: str) -> float:
        """Calculate score based on medical entity detection."""
        entity_score = 0.0
        
        # Check for medication patterns
        for pattern in self.medication_patterns:
            if pattern.search(sentence_lower):
                entity_score += 0.3
        
        # Check for specific medical entities
        medical_entities = [
            'patient', 'doctor', 'physician', 'nurse', 'hospital', 'clinic',
            'diagnosis', 'treatment', 'medication', 'surgery', 'procedure'
        ]
        
        for entity in medical_entities:
            if entity in sentence_lower:
                entity_score += 0.1
        
        return min(entity_score, 1.0)
    
    def _calculate_pattern_score(self, sentence_lower: str) -> float:
        """Calculate score based on medical pattern matching."""
        pattern_score = 0.0
        
        for pattern in self.medical_patterns:
            matches = pattern.findall(sentence_lower)
            if matches:
                pattern_score += len(matches) * 0.2
        
        return min(pattern_score, 1.0)
    
    def _calculate_context_score(self, sentence_lower: str) -> float:
        """Calculate score based on medical context indicators."""
        context_indicators = [
            'health', 'medical', 'clinical', 'therapeutic', 'diagnostic',
            'pathological', 'physiological', 'anatomical', 'surgical',
            'pharmaceutical', 'medicinal', 'remedy', 'cure', 'heal'
        ]
        
        context_score = 0.0
        for indicator in context_indicators:
            if indicator in sentence_lower:
                context_score += 0.2
        
        return min(context_score, 1.0)
    
    def get_health_analysis(self, sentence: str) -> Dict[str, Any]:
        """
        Get detailed health domain analysis for a sentence.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            Dictionary with detailed health analysis
        """
        if not sentence or not sentence.strip():
            return {
                'health_score': 0.0,
                'medical_terms': [],
                'medical_patterns': [],
                'entities_found': 0,
                'relevance_level': 'none'
            }
        
        sentence_lower = sentence.lower()
        words = sentence_lower.split()
        
        # Find medical terms
        found_terms = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.medical_terms:
                found_terms.append(clean_word)
        
        # Find medical patterns
        found_patterns = []
        for pattern in self.medical_patterns:
            matches = pattern.findall(sentence_lower)
            found_patterns.extend(matches)
        
        # Calculate overall score
        health_score = self.score_health_relevance(sentence)
        
        # Determine relevance level
        if health_score >= 0.8:
            relevance_level = 'high'
        elif health_score >= 0.5:
            relevance_level = 'medium'
        elif health_score >= 0.3:
            relevance_level = 'low'
        else:
            relevance_level = 'none'
        
        return {
            'health_score': health_score,
            'medical_terms': found_terms,
            'medical_patterns': found_patterns,
            'entities_found': len(found_terms),
            'relevance_level': relevance_level
        }
    
    def get_filtering_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the health filtering process.
        
        Returns:
            Dictionary containing health filtering statistics
        """
        return {
            'total_processed': self.stats['total_processed'],
            'health_relevant': self.stats['health_relevant'],
            'relevance_rate': self.stats['health_relevant'] / self.stats['total_processed'] if self.stats['total_processed'] > 0 else 0,
            'medical_entities_found': self.stats['medical_entities_found'],
            'relevance_breakdown': {
                'high_relevance': self.stats['high_relevance'],
                'medium_relevance': self.stats['medium_relevance'],
                'low_relevance': self.stats['low_relevance']
            },
            'threshold_used': self.health_threshold
        }
    
    def reset_stats(self):
        """Reset filtering statistics."""
        self.stats = {
            'total_processed': 0,
            'health_relevant': 0,
            'medical_entities_found': 0,
            'high_relevance': 0,
            'medium_relevance': 0,
            'low_relevance': 0
        }
