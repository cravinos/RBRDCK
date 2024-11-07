from typing import Dict, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ComplianceRule:
    id: str
    name: str
    description: str
    severity: str
    category: str
    check_function: callable

@dataclass
class ComplianceViolation:
    rule_id: str
    description: str
    severity: str
    file_path: str
    line_number: Optional[int]
    context: Dict

class ComplianceManager:
    def __init__(self):
        self.rules: Dict[str, ComplianceRule] = {}
        self.audit_logger = AuditLogger()
        self.policy_engine = PolicyEngine()
        
    def add_rule(self, rule: ComplianceRule):
        """Add a compliance rule."""
        self.rules[rule.id] = rule
        logger.info(f"Added compliance rule: {rule.id}")
        
    def check_compliance(self, pr: PullRequest) -> Dict:
        """Check PR against compliance policies."""
        try:
            violations = []
            context = self._build_compliance_context(pr)
            
            for rule in self.rules.values():
                try:
                    rule_violations = rule.check_function(context)
                    if rule_violations:
                        violations.extend([
                            ComplianceViolation(
                                rule_id=rule.id,
                                description=v.get("description"),
                                severity=rule.severity,
                                file_path=v.get("file_path"),
                                line_number=v.get("line_number"),
                                context=v.get("context", {})
                            ) for v in rule_violations
                        ])
                except Exception as e:
                    logger.error(f"Error checking rule {rule.id}: {e}")
                    
            report = self._generate_compliance_report(violations)
            self.audit_logger.log_compliance_check(pr.number, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in compliance check: {e}")
            raise
            
    def _build_compliance_context(self, pr: PullRequest) -> Dict:
        """Build context for compliance checking."""
        return {
            "pr_number": pr.number,
            "author": pr.user.login,
            "files_changed": [f.filename for f in pr.get_files()],
            "diff": pr.get_diff(),
            "base_branch": pr.base.ref,
            "created_at": pr.created_at,
            "labels": [l.name for l in pr.get_labels()],
            "reviewers": [r.login for r in pr.get_reviewers()]
        }
        
    def _generate_compliance_report(self, violations: List[ComplianceViolation]) -> Dict:
        """Generate compliance report from violations."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_violations": len(violations),
            "violations_by_severity": self._group_violations_by_severity(violations),
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "description": v.description,
                    "severity": v.severity,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "context": v.context
                } for v in violations
            ],
            "summary": self._generate_violation_summary(violations)
        }
        
    def _group_violations_by_severity(self, violations: List[ComplianceViolation]) -> Dict:
        """Group violations by severity level."""
        severity_groups = {}
        for violation in violations:
            if violation.severity not in severity_groups:
                severity_groups[violation.severity] = 0
            severity_groups[violation.severity] += 1
        return severity_groups
        
    def _generate_violation_summary(self, violations: List[ComplianceViolation]) -> str:
        """Generate a human-readable summary of violations."""
        if not violations:
            return "No compliance violations found."
            
        severity_counts = self._group_violations_by_severity(violations)
        summary_parts = [
            f"Found {len(violations)} compliance violations:",
            *[f"- {severity}: {count} violation(s)" 
              for severity, count in severity_counts.items()]
        ]
        return "\n".join(summary_parts)