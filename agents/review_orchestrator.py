# agents/review_orchestrator.py

from typing import Dict, List
from agents.base_review_agent import BaseReviewAgent
from agents.documentation_review_agent import DocumentationReviewAgent
from agents.code_quality_agent import CodeQualityAgent
from agents.test_coverage_agent import TestCoverageAgent
from agents.dependency_review_agent import DependencyReviewAgent
from github.PullRequest import PullRequest
import logging

logger = logging.getLogger(__name__)

class ReviewContext:
    """Maintains shared context between review agents."""
    
    def __init__(self, pr: PullRequest, diff: str, previous_comments: str):
        self.pr = pr
        self.diff = diff
        self.previous_comments = previous_comments
        self.reviews: Dict[str, Dict] = {}
        self.shared_insights: List[Dict] = []
        
    def add_review(self, agent_type: str, review: Dict):
        """Adds a review from an agent to the shared context."""
        self.reviews[agent_type] = review
        
    def add_insight(self, agent_type: str, insight: Dict):
        """Adds an insight that other agents should consider."""
        self.shared_insights.append({
            "agent": agent_type,
            "insight": insight
        })
        
    def get_agent_review(self, agent_type: str) -> Dict:
        """Gets a specific agent's review."""
        return self.reviews.get(agent_type, {})
        
    def get_all_reviews(self) -> Dict[str, Dict]:
        """Gets all agent reviews."""
        return self.reviews
        
    def get_insights(self) -> List[Dict]:
        """Gets all shared insights."""
        return self.shared_insights

class ReviewOrchestrator:
    """Orchestrates the collaborative review process between agents."""
    
    def __init__(self):
        self.agents = {
            'documentation': DocumentationReviewAgent(),
            'code_quality': CodeQualityAgent(),
            'test_coverage': TestCoverageAgent(),
            'dependencies': DependencyReviewAgent()
        }
        
    def conduct_collaborative_review(self, context: ReviewContext) -> str:
        """
        Conducts a collaborative review where agents share insights and build upon each other's findings.
        
        Args:
            context: ReviewContext object containing PR information and shared context
            
        Returns:
            str: Aggregated review comments
        """
        # Phase 1: Initial Reviews
        self._conduct_initial_reviews(context)
        
        # Phase 2: Cross-Reference and Enhancement
        self._enhance_reviews_with_shared_insights(context)
        
        # Phase 3: Generate Final Report
        return self._generate_final_report(context)
        
    def _conduct_initial_reviews(self, context: ReviewContext):
        """Conducts initial reviews from all agents."""
        for agent_type, agent in self.agents.items():
            try:
                if agent_type == 'documentation':
                    review = agent.review_documentation(context.diff, context.previous_comments)
                elif agent_type == 'code_quality':
                    review = agent.review_code_quality(context.pr, context.diff, context.previous_comments)
                elif agent_type == 'test_coverage':
                    review = agent.review_test_coverage(context.pr, context.diff, context.previous_comments)
                elif agent_type == 'dependencies':
                    review = agent.review_dependencies(context.pr, context.diff, context.previous_comments)
                    
                context.add_review(agent_type, review)
                
                # Extract key insights for other agents
                self._share_agent_insights(agent_type, review, context)
                    
            except Exception as e:
                logger.error(f"Error in {agent_type} review: {e}", exc_info=True)
                
    def _share_agent_insights(self, agent_type: str, review: Dict, context: ReviewContext):
        """Extracts and shares key insights from an agent's review."""
        if agent_type == 'code_quality':
            if review.get('complexity', {}).get('high_complexity_files', []):
                context.add_insight('code_quality', {
                    'type': 'high_complexity',
                    'files': review['complexity']['high_complexity_files']
                })
                
        elif agent_type == 'test_coverage':
            if review.get('untested_files', []):
                context.add_insight('test_coverage', {
                    'type': 'untested_files',
                    'files': review['untested_files']
                })
                
        elif agent_type == 'dependencies':
            if review.get('security_alerts', []):
                context.add_insight('dependencies', {
                    'type': 'security_concerns',
                    'alerts': review['security_alerts']
                })
                
    def _enhance_reviews_with_shared_insights(self, context: ReviewContext):
        """Enhances reviews based on insights from other agents."""
        for agent_type, agent in self.agents.items():
            try:
                review = context.get_agent_review(agent_type)
                if not review:
                    continue
                    
                enhanced_review = self._apply_cross_agent_insights(
                    agent_type, review, context.get_insights())
                context.add_review(agent_type, enhanced_review)
                
            except Exception as e:
                logger.error(f"Error enhancing {agent_type} review: {e}", exc_info=True)
                
    def _apply_cross_agent_insights(self, agent_type: str, review: Dict, insights: List[Dict]) -> Dict:
        """Applies insights from other agents to enhance a review."""
        enhanced_review = review.copy()
        
        if agent_type == 'documentation':
            # Documentation agent considers complexity and test coverage insights
            for insight in insights:
                if insight['agent'] == 'code_quality' and insight['insight']['type'] == 'high_complexity':
                    files = insight['insight']['files']
                    enhanced_review.setdefault('suggestions', []).append(
                        f"Consider adding detailed documentation for high complexity files: {', '.join(files)}")
                    
        elif agent_type == 'test_coverage':
            # Test coverage agent considers security insights
            for insight in insights:
                if insight['agent'] == 'dependencies' and insight['insight']['type'] == 'security_concerns':
                    enhanced_review.setdefault('suggestions', []).append(
                        "Add security-focused test cases to verify proper handling of dependencies with security concerns")
                    
        return enhanced_review
        
    def _generate_final_report(self, context: ReviewContext) -> str:
        """Generates a comprehensive final report combining all reviews."""
        sections = []
        
        # Add summary section
        sections.append("# Pull Request Review Summary\n")
        sections.append("## Overview\n")
        sections.append(self._generate_overview_section(context))
        
        # Add detailed findings from each agent
        for agent_type, review in context.get_all_reviews().items():
            sections.append(f"\n## {agent_type.replace('_', ' ').title()} Review\n")
            sections.append(self._format_agent_review(agent_type, review))
            
        # Add cross-cutting concerns section
        sections.append("\n## Cross-Cutting Concerns\n")
        sections.append(self._generate_cross_cutting_concerns(context))
        
        # Add recommendations section
        sections.append("\n## Key Recommendations\n")
        sections.append(self._generate_recommendations(context))
        
        return "\n".join(sections)
        
    def _generate_overview_section(self, context: ReviewContext) -> str:
        """Generates the overview section of the report."""
        overview = []
        all_reviews = context.get_all_reviews()
        
        # Calculate overall statistics
        total_issues = sum(len(review.get('suggestions', [])) for review in all_reviews.values())
        security_concerns = len([i for i in context.get_insights() 
                               if i['agent'] == 'dependencies' and 
                               i['insight']['type'] == 'security_concerns'])
        
        overview.append(f"- Total Issues Found: {total_issues}")
        overview.append(f"- Security Concerns: {security_concerns}")
        overview.append(f"- Reviewed Aspects: {', '.join(all_reviews.keys())}")
        
        return "\n".join(overview)
        
    def _format_agent_review(self, agent_type: str, review: Dict) -> str:
        """Formats an individual agent's review for the final report."""
        sections = []
        
        if agent_type == 'code_quality':
            sections.append("### Code Quality Metrics")
            metrics = review.get('summary', {})
            sections.append(f"- Complexity Score: {metrics.get('average_complexity', 'N/A')}")
            sections.append(f"- High Complexity Files: {metrics.get('high_complexity_files', 0)}")
            
        elif agent_type == 'test_coverage':
            sections.append("### Test Coverage Analysis")
            coverage = review.get('summary', {})
            sections.append(f"- Coverage Ratio: {coverage.get('test_coverage_ratio', 0):.2f}")
            sections.append(f"- Untested Files: {coverage.get('untested_files_count', 0)}")
            
        # Add suggestions
        if review.get('suggestions'):
            sections.append("\n### Suggestions")
            for suggestion in review['suggestions']:
                sections.append(f"- {suggestion}")
                
        return "\n".join(sections)
        
    def _generate_cross_cutting_concerns(self, context: ReviewContext) -> str:
        """Generates the cross-cutting concerns section."""
        concerns = []
        insights = context.get_insights()
        
        for insight in insights:
            if insight['agent'] == 'code_quality' and insight['insight']['type'] == 'high_complexity':
                concerns.append("- High code complexity may affect maintainability and testing effort")
            elif insight['agent'] == 'dependencies' and insight['insight']['type'] == 'security_concerns':
                concerns.append("- Security vulnerabilities in dependencies require immediate attention")
                
        return "\n".join(concerns) if concerns else "No significant cross-cutting concerns identified."
        
    def _generate_recommendations(self, context: ReviewContext) -> str:
        """Generates key recommendations based on all reviews and insights."""
        recommendations = []
        all_reviews = context.get_all_reviews()
        
        # Prioritize security concerns
        if any(i['agent'] == 'dependencies' and i['insight']['type'] == 'security_concerns' 
               for i in context.get_insights()):
            recommendations.append("1. Address identified security vulnerabilities in dependencies")
            
        # Add high-priority suggestions from each agent
        for agent_type, review in all_reviews.items():
            if suggestions := review.get('suggestions', []):
                recommendations.append(f"\nPriority items from {agent_type} review:")
                recommendations.extend(f"- {suggestion}" for suggestion in suggestions[:3])
                
        return "\n".join(recommendations)