from typing import Dict, List
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Policy:
    id: str
    name: str
    rules: List[Dict]
    severity: str
    enabled: bool = True

class PolicyEngine:
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        
    def add_policy(self, policy: Policy):
        """Add or update a policy."""
        self.policies[policy.id] = policy
        logger.info(f"Added policy: {policy.id}")
        
    def remove_policy(self, policy_id: str):
        """Remove a policy."""
        if policy_id in self.policies:
            del self.policies[policy_id]
            logger.info(f"Removed policy: {policy_id}")
            
    def validate(self, context: Dict) -> List[Dict]:
        """Validate context against all enabled policies."""
        violations = []
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            try:
                policy_violations = self._check_policy(policy, context)
                violations.extend(policy_violations)
            except Exception as e:
                logger.error(f"Error checking policy {policy.id}: {e}")
                
        return violations
        
    def _check_policy(self, policy: Policy, context: Dict) -> List[Dict]:
        """Check a single policy against the context."""
        violations = []
        
        for rule in policy.rules:
            try:
                if not self._evaluate_rule(rule, context):
                    violations.append({
                        "policy_id": policy.id,
                        "policy_name": policy.name,
                        "rule_id": rule["id"],
                        "description": rule["description"],
                        "severity": policy.severity
                    })
            except Exception as e:
                logger.error(f"Error evaluating rule {rule['id']}: {e}")
                
        return violations
        
    def _evaluate_rule(self, rule: Dict, context: Dict) -> bool:
        """Evaluate a single rule against the context."""
        condition = rule["condition"]
        
        if condition["type"] == "regex":
            return self._evaluate_regex(condition["pattern"], context.get(condition["field"], ""))
        elif condition["type"] == "threshold":
            return self._evaluate_threshold(condition["value"], context.get(condition["field"], 0))
        elif condition["type"] == "required":
            return condition["field"] in context
        else:
            raise ValueError(f"Unknown condition type: {condition['type']}")
            
    def _evaluate_regex(self, pattern: str, value: str) -> bool:
        """Evaluate regex pattern."""
        import re
        return bool(re.match(pattern, str(value)))
        
    def _evaluate_threshold(self, threshold: float, value: float) -> bool:
        """Evaluate threshold condition."""
        return float(value) <= threshold