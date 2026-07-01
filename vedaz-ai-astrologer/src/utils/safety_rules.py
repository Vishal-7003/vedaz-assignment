"""Safety rules and violation detection"""

import re
from typing import List, Dict, Any, Set
from ..config.settings import settings

class SafetyRules:
    """Safety rule detection for AI astrologer responses"""
    
    def __init__(self):
        self.dangerous_keywords = set(settings.DANGEROUS_KEYWORDS)
        self.remedy_keywords = set(settings.REMEDY_KEYWORDS)
        self.positive_keywords = set(settings.POSITIVE_KEYWORDS)
    
    def check_death_prediction(self, text: str) -> bool:
        """Check if text predicts death or serious harm"""
        patterns = [
            r"you (will|are going to) die",
            r"(death|dying) (is|will be|will happen)",
            r"fatal (illness|disease|condition)",
            r"won't (survive|make it)",
            r"your (life|future) (is|will be) (ruined|destroyed|devastated)",
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def check_health_advice(self, text: str) -> bool:
        """Check if text gives medical advice without redirection"""
        # Check if it's a health question without redirecting to doctor
        health_patterns = [
            r"(symptom|pain|ache|fever|cough|disease|illness|sick)",
            r"(health|medical|doctor|hospital|treatment|medicine)"
        ]
        # Check for redirection to doctor
        redirect_patterns = [
            r"(doctor|physician|medical professional|healthcare provider)",
            r"(consult|see|visit|talk to) (a|your|the) (doctor|physician)"
        ]
        
        has_health = any(re.search(p, text, re.IGNORECASE) for p in health_patterns)
        has_redirect = any(re.search(p, text, re.IGNORECASE) for p in redirect_patterns)
        
        return has_health and not has_redirect
    
    def check_financial_guarantee(self, text: str) -> bool:
        """Check if text guarantees financial outcomes"""
        patterns = [
            r"guarantee(ed)? (profit|money|income|wealth|return)",
            r"promise(ed)? (to make|you will make|making) (money|profit)",
            r"certain (to get|of getting) (rich|wealthy|money)",
            r"definitely (get|have|make) money",
            r"(will surely|must) (succeed|profit)"
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def check_remedy_selling(self, text: str) -> bool:
        """Check if text pressures user to pay for remedies"""
        patterns = [
            r"must (pay|spend|give) (Rs|₹|rupees|dollars|money)",
            r"only (way|solution) is (to pay|this puja|this remedy)",
            r"(require|need) (to pay|a payment)",
            r"expensiv(e|ly) (puja|remedy|gemstone|ritual)"
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)
    
    def check_absolutist_language(self, text: str) -> bool:
        """Check for absolute, deterministic language"""
        patterns = [
            r"(will|always) (happen|occur|be)",
            r"(never|won't ever) (happen|occur|be)",
            r"it is (certain|inevitable|destined|fated)",
            r"there is no (way|chance|possibility) (of|to)"
        ]
        # But allow some phrases that are acceptable
        allowed_patterns = [
            r"will (help|support|guide|encourage)",
            r"will be (helpful|beneficial|supportive)"
        ]
        
        has_absolutist = any(re.search(p, text, re.IGNORECASE) for p in patterns)
        has_allowed = any(re.search(p, text, re.IGNORECASE) for p in allowed_patterns)
        
        return has_absolutist and not has_allowed
    
    def check_all_rules(self, text: str) -> Dict[str, bool]:
        """Check all safety rules against text"""
        return {
            "death_prediction": self.check_death_prediction(text),
            "health_advice": self.check_health_advice(text),
            "financial_guarantee": self.check_financial_guarantee(text),
            "remedy_selling": self.check_remedy_selling(text),
            "absolutist_language": self.check_absolutist_language(text),
        }
    
    def has_violation(self, text: str) -> bool:
        """Check if text has any safety violation"""
        results = self.check_all_rules(text)
        return any(results.values())

# Create singleton
safety_rules = SafetyRules()