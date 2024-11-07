import requests
from github.Repository import Repository
from github.PullRequest import PullRequest
import logging
from config import GITHUB_TOKEN
from typing import List, Dict, Optional, Union
import re
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

def get_open_pull_requests(repo):
    try:
        pulls = repo.get_pulls(state='open', sort='created')
        return list(pulls)
    except Exception as e:
        logger.error(f"Error fetching pull requests: {e}")
        return []

def get_pull_request_diff(pr: PullRequest):
    try:
        headers = {
            'Accept': 'application/vnd.github.v3.diff',
            'Authorization': f'token {GITHUB_TOKEN}'
        }
        response = requests.get(pr.diff_url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error fetching diff for PR #{pr.number}: {e}")
        return ""

def parse_review_comments(review_body: str) -> List[Dict]:
    """
    Parses the LLM's review and extracts individual comments with file paths and line numbers.
    """
    comments = []
    pattern = re.compile(
        r"- \*\*Issue Description\*\*\n\n(.+?)\n\n\*\*Suggestion:\*\*\n\n```suggestion\n(.+?)\n```\n\n\*\*File:\*\* `(.+?)`\n\n\*\*Line:\*\* (\d+)",
        re.DOTALL
    )
    matches = pattern.findall(review_body)
    for match in matches:
        issue_description, suggestion, file_path, line_number = match
        comments.append({
            'body': f"{issue_description}\n\n```suggestion\n{suggestion}\n```",
            'path': file_path,
            'line': int(line_number),
        })
    return comments

def post_review_comment(pr: PullRequest, review_body: str):
    try:
        if not review_body.strip():
            logger.error("Review body is empty. Skipping review post.")
            return

        comments_data = parse_review_comments(review_body)
        if comments_data:
            review_comments = []
            for comment in comments_data:
                position = get_diff_position(pr, comment['path'], comment['line'])
                if position is not None:
                    review_comments.append({
                        'path': comment['path'],
                        'position': position,
                        'body': comment['body'],
                    })
                else:
                    logger.warning(f"Could not find position for comment: {comment}")
            
            if review_comments:
                pr.create_review(
                    body="Please see the suggested changes below:",
                    event='COMMENT',
                    comments=review_comments,
                )
                logger.info(f"Posted review with {len(review_comments)} comments for PR #{pr.number}")
            else:
                logger.warning(f"No valid comments to post for PR #{pr.number}")
        else:
            # Fallback to a general comment if parsing fails, but ensure it's not empty
            if review_body.strip():
                pr.create_issue_comment(review_body)
                logger.info(f"Posted general comment for PR #{pr.number}")
            else:
                logger.warning(f"No content to post for PR #{pr.number}")
    except Exception as e:
        logger.error(f"Error posting review for PR #{pr.number}: {e}", exc_info=True)

def get_diff_position(pr: PullRequest, file_path: str, line_number: int) -> int:
    """
    Maps a line number in the file to a position in the diff.
    """
    try:
        files = pr.get_files()
        for file in files:
            if file.filename == file_path:
                patch = file.patch
                # Parse the patch to map line numbers to positions
                position = map_line_to_position(patch, line_number)
                if position:
                    return position
        logger.error(f"Could not find position for {file_path}:{line_number}")
        return None
    except Exception as e:
        logger.error(f"Error getting diff position: {e}")
        return None

def map_line_to_position(patch: str, line_number: int) -> int:
    """
    Parses the patch text to find the diff position of the given line number.
    """
    current_line = None
    position = 0
    for line in patch.split('\n'):
        if line.startswith('@@'):
            # Parse the hunk header to get the starting line number
            m = re.match(r'@@ \-\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if m:
                current_line = int(m.group(1)) - 1
        elif line.startswith('+'):
            current_line += 1
            position += 1
            if current_line == line_number:
                return position
        elif not line.startswith('-'):
            current_line += 1
            position += 1
    return None
def get_previous_comments(pr: PullRequest) -> str:
    """
    Fetches previous comments on a pull request.
    
    Args:
    pr (PullRequest): The pull request object.
    
    Returns:
    str: A formatted string containing previous comments.
    """
    comments = pr.get_issue_comments()
    formatted_comments = []
    for comment in comments:
        formatted_comments.append(f"Commenter: {comment.user.login}\nComment: {comment.body}\n")
    
    return "\n".join(formatted_comments)

def analyze_code_quality(pr: PullRequest) -> Dict:
    """
    Analyzes code quality metrics for files in a pull request.
    
    Args:
        pr: PullRequest object
        
    Returns:
        Dictionary containing various code quality metrics and analysis
    """
    try:
        files = list(pr.get_files())
        metrics = {
            'code_style': {},
            'complexity': {},
            'potential_issues': [],
            'summary': {},
            'suggestions': []
        }
        
        total_lines_changed = 0
        file_count = len(files)
        
        for file in files:
            if file.filename.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.cs', '.go', '.rb')):
                patch = file.patch if file.patch else ''
                lines = patch.split('\n')
                total_lines_changed += len(lines)
                
                # Code style analysis
                style_issues = []
                
                # Check file size
                if len(lines) > 300:
                    style_issues.append({
                        'issue': 'Large file changes',
                        'severity': 'warning',
                        'suggestion': 'Consider breaking down large changes into smaller, focused PRs'
                    })
                
                # Check for debug statements
                debug_patterns = {
                    'python': [r'print\(', r'debugger', r'breakpoint\(\)'],
                    'javascript': [r'console\.(log|debug|info)', r'debugger'],
                    'java': [r'System\.out\.print', r'e\.printStackTrace\(\)'],
                }
                
                file_ext = file.filename.split('.')[-1]
                for lang, patterns in debug_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, patch):
                            style_issues.append({
                                'issue': f'Contains debug statements ({pattern})',
                                'severity': 'info',
                                'suggestion': 'Remove debug statements before merging'
                            })
                
                # Check for TODO comments
                todos = re.findall(r'(?i)(TODO|FIXME|XXX|HACK):', patch)
                if todos:
                    style_issues.append({
                        'issue': f'Contains {len(todos)} TODO/FIXME comments',
                        'severity': 'info',
                        'suggestion': 'Consider addressing TODOs or creating issues for tracking'
                    })
                
                # Code complexity analysis
                complexity_metrics = {
                    'cognitive_complexity': 0,
                    'nested_depth': 0,
                    'function_count': len(re.findall(r'(def\s+|function\s+|class\s+)', patch)),
                }
                
                # Calculate cognitive complexity
                complexity_metrics['cognitive_complexity'] += patch.count('if ') * 1
                complexity_metrics['cognitive_complexity'] += patch.count('else ') * 1
                complexity_metrics['cognitive_complexity'] += patch.count('for ') * 2
                complexity_metrics['cognitive_complexity'] += patch.count('while ') * 2
                complexity_metrics['cognitive_complexity'] += patch.count('try') * 1
                complexity_metrics['cognitive_complexity'] += patch.count('catch') * 1
                
                # Calculate maximum nesting depth
                current_depth = 0
                max_depth = 0
                for line in lines:
                    if re.search(r'^\s*(if|for|while|def|class)', line):
                        current_depth += 1
                        max_depth = max(max_depth, current_depth)
                    elif re.search(r'^\s*}|\s*end\s*$', line):
                        current_depth = max(0, current_depth - 1)
                
                complexity_metrics['nested_depth'] = max_depth
                
                if complexity_metrics['cognitive_complexity'] > 15:
                    metrics['suggestions'].append({
                        'file': file.filename,
                        'suggestion': 'High cognitive complexity. Consider breaking down complex logic.',
                        'severity': 'warning'
                    })
                
                if max_depth > 4:
                    metrics['suggestions'].append({
                        'file': file.filename,
                        'suggestion': 'Deep nesting detected. Consider extracting methods or simplifying logic.',
                        'severity': 'warning'
                    })
                
                metrics['code_style'][file.filename] = style_issues
                metrics['complexity'][file.filename] = complexity_metrics
                
                # Check for potential issues
                security_patterns = [
                    (r'password|secret|key|token|credential', 'Possible sensitive information'),
                    (r'sql\s*=|SELECT\s+.*\s+FROM', 'SQL query detected - verify for injection risks'),
                    (r'eval\(|exec\(', 'Dangerous code execution detected'),
                    (r'subprocess|shell|os\.system', 'System command execution detected'),
                ]
                
                for pattern, message in security_patterns:
                    if re.search(pattern, patch, re.IGNORECASE):
                        metrics['potential_issues'].append({
                            'file': file.filename,
                            'issue': message,
                            'severity': 'high',
                            'line_numbers': [i + 1 for i, line in enumerate(lines) 
                                          if re.search(pattern, line, re.IGNORECASE)]
                        })
        
        # Generate summary
        metrics['summary'] = {
            'files_changed': file_count,
            'total_lines_changed': total_lines_changed,
            'average_complexity': sum(m['cognitive_complexity'] for m in metrics['complexity'].values()) / max(len(metrics['complexity']), 1),
            'high_complexity_files': sum(1 for m in metrics['complexity'].values() if m['cognitive_complexity'] > 15),
            'security_concerns': len(metrics['potential_issues']),
            'style_issues': sum(len(issues) for issues in metrics['code_style'].values())
        }
        
        return metrics
    except Exception as e:
        logger.error(f"Error analyzing code quality: {e}")
        return {}

def get_test_coverage(pr: PullRequest) -> Dict:
    """
    Analyzes test coverage for changes in a pull request.
    
    Args:
        pr: PullRequest object
        
    Returns:
        Dictionary containing test coverage analysis and suggestions
    """
    try:
        files = list(pr.get_files())
        coverage_info = {
            'has_test_changes': False,
            'source_files': [],
            'test_files': [],
            'untested_files': [],
            'test_ratio': 0.0,
            'suggestions': [],
            'coverage_gaps': [],
            'summary': {}
        }
        
        test_patterns = {
            'python': [r'test_.*\.py$', r'.*_test\.py$', r'.*_spec\.py$'],
            'javascript': [r'.*\.test\.(js|ts)$', r'.*\.spec\.(js|ts)$', r'__tests__/.*\.(js|ts)$'],
            'java': [r'.*Test\.java$', r'.*Tests\.java$', r'.*IT\.java$'],
            'ruby': [r'.*_test\.rb$', r'.*_spec\.rb$'],
            'go': [r'.*_test\.go$'],
        }
        
        source_files_map = {}  # Maps source files to their corresponding test files
        
        for file in files:
            file_path = file.filename
            
            # Determine if it's a test file
            is_test_file = False
            for lang, patterns in test_patterns.items():
                if any(re.match(pattern, file_path) for pattern in patterns):
                    is_test_file = True
                    coverage_info['test_files'].append({
                        'path': file_path,
                        'language': lang,
                        'additions': file.additions,
                        'deletions': file.deletions
                    })
                    break
            
            if is_test_file:
                coverage_info['has_test_changes'] = True
                # Try to find corresponding source file
                possible_source = re.sub(r'_test\.|_spec\.|Test\.|Tests\.', '.', file_path)
                source_files_map[possible_source] = file_path
            else:
                # It's a source file
                if file_path.endswith(('.py', '.js', '.ts', '.java', '.go', '.rb')):
                    coverage_info['source_files'].append({
                        'path': file_path,
                        'additions': file.additions,
                        'deletions': file.deletions
                    })
                    
                    # Check for corresponding test file
                    has_test = False
                    repo = pr.base.repo
                    
                    # Generate possible test file names
                    test_file_candidates = []
                    file_name = file_path.rsplit('.', 1)[0]
                    extension = file_path.rsplit('.', 1)[1]
                    
                    if extension == 'py':
                        test_file_candidates = [
                            f'test_{file_path}',
                            f'{file_name}_test.py',
                            f'tests/{file_path}',
                            f'test/{file_path}'
                        ]
                    elif extension in ('js', 'ts'):
                        test_file_candidates = [
                            f'{file_name}.test.{extension}',
                            f'{file_name}.spec.{extension}',
                            f'__tests__/{file_path}'
                        ]
                    elif extension == 'java':
                        test_file_candidates = [
                            f'{file_name}Test.java',
                            f'{file_name}Tests.java',
                            f'test/java/{file_path}'
                        ]
                    
                    for test_file in test_file_candidates:
                        try:
                            repo.get_contents(test_file)
                            has_test = True
                            source_files_map[file_path] = test_file
                            break
                        except:
                            continue
                    
                    if not has_test:
                        coverage_info['untested_files'].append(file_path)
                        coverage_info['coverage_gaps'].append({
                            'file': file_path,
                            'suggestion': f'Missing test file. Consider adding tests in one of: {", ".join(test_file_candidates)}',
                            'severity': 'warning'
                        })
        
        # Calculate metrics
        if coverage_info['source_files']:
            coverage_info['test_ratio'] = len(coverage_info['test_files']) / len(coverage_info['source_files'])
            
            if coverage_info['test_ratio'] < 0.5:
                coverage_info['suggestions'].append({
                    'suggestion': 'Low test coverage ratio. Consider adding more tests.',
                    'severity': 'warning',
                    'details': f'Current ratio: {coverage_info["test_ratio"]:.2f}'
                })
        
        # Generate summary
        coverage_info['summary'] = {
            'total_source_files': len(coverage_info['source_files']),
            'total_test_files': len(coverage_info['test_files']),
            'untested_files_count': len(coverage_info['untested_files']),
            'test_coverage_ratio': coverage_info['test_ratio'],
            'has_new_tests': coverage_info['has_test_changes'],
            'coverage_gaps_count': len(coverage_info['coverage_gaps'])
        }
        
        return coverage_info
    except Exception as e:
        logger.error(f"Error analyzing test coverage: {e}")
        return {}

def analyze_dependencies(pr: PullRequest) -> Dict:
    """
    Analyzes dependency changes in package management files.
    
    Args:
        pr: PullRequest object
        
    Returns:
        Dictionary containing dependency analysis and security implications
    """
    try:
        files = list(pr.get_files())
        
        dependency_files = {
            'python': ['requirements.txt', 'setup.py', 'Pipfile', 'pyproject.toml'],
            'node': ['package.json', 'package-lock.json', 'yarn.lock'],
            'java': ['pom.xml', 'build.gradle', 'gradle.build'],
            'dotnet': ['*.csproj', 'packages.config'],
            'ruby': ['Gemfile', 'Gemfile.lock'],
            'go': ['go.mod', 'go.sum'],
        }
        
        analysis = {
            'dependency_files_changed': [],
            'added_dependencies': [],
            'removed_dependencies': [],
            'updated_dependencies': [],
            'security_alerts': [],
            'license_alerts': [],
            'suggestions': [],
            'summary': {}
        }
        
        for file in files:
            filename = file.filename.lower()
            
            # Identify dependency file type
            for tech, dep_files in dependency_files.items():
                if any(dep_file.lower() in filename for dep_file in dep_files):
                    analysis['dependency_files_changed'].append({
                        'file': file.filename,
                        'technology': tech
                    })
                    
                    patch = file.patch if file.patch else ''
                    
                    # Parse dependencies based on file type
                    if tech == 'python':
                        if 'requirements.txt' in filename:
                            # Parse requirements.txt format
                            added = re.findall(r'^\+([a-zA-Z0-9-_.]+)==([^=\n]+)$', patch, re.MULTILINE)
                            removed = re.findall(r'^\-([a-zA-Z0-9-_.]+)==([^=\n]+)$', patch, re.MULTILINE)
                            
                            for dep, version in added:
                                analysis['added_dependencies'].append({
                                    'name': dep,
                                    'version': version,
                                    'file': filename
                                })
                            
                            for dep, version in removed:
                                analysis['removed_dependencies'].append({
                                    'name': dep,
                                    'version': version,
                                    'file': filename
                                })
                                
                    elif tech == 'node':
                        if 'package.json' in filename:
                            # Parse package.json dependencies
                            added = re.findall(r'^\+"([^"]+)":\s*"([^"]+)"', patch, re.MULTILINE)
                            removed = re.findall(r'^\-"([^"]+)":\s*"([^"]+)"', patch, re.MULTILINE)
                            
                            for dep, version in added:
                                analysis['added_dependencies'].append({
                                    'name': dep,
                                    'version': version,
                                    'file': filename
                                })
                            
                            for dep, version in removed:
                                analysis['removed_dependencies'].append({
                                    'name': dep,
                                    'version': version,
                                    'file': filename
                                })
                    
                    # Security checks
                    security_patterns = [
                        (r'alpha|beta|rc|snapshot', 'Pre-release dependency detected'),
                        (r'>=|^[~^]', 'Loose version constraint detected'),
                        (r'0\.[0-9]+\.', 'Early version (0.x) dependency detected'),
                        (r'file:|git\+|git://', 'Non-registry dependency source detected'),
                        (r'http:', 'Insecure HTTP dependency source detected')
                    ]
                    
                    for pattern, message in security_patterns:
                        if re.search(pattern, patch):
                            analysis['security_alerts'].append({
                                'file': filename,
                                'alert': message,
                                'severity': 'warning',
                                'suggestion': 'Consider using stable versions from official package registries'
                            })
                    
                    # Check for major version updates
                    for dep in analysis['added_dependencies']:
                        removed_dep = next(
                            (d for d in analysis['removed_dependencies'] if d['name'] == dep['name']),
                            None
                        )
                        if removed_dep:
                            old_version = removed_dep['version']
                            new_version = dep['version']
                            
                            # Try to extract major versions
                            old_major = re.search(r'^(\d+)', old_version)
                            new_major = re.search(r'^(\d+)', new_version)
                            
                            if old_major and new_major:
                                if int(new_major.group(1)) > int(old_major.group(1)):
                                    analysis['updated_dependencies'].append({
                                        'name': dep['name'],
                                        'old_version': old_version,
                                        'new_version': new_version,
                                        'change_type': 'major',
                                        'file': filename
                                    })
                                    
                                    analysis['suggestions'].append({
                                        'suggestion': f'Major version update for {dep["name"]} ({old_version} → {new_version}). Review changelog for breaking changes.',
                                        'severity': 'warning'
                                    })
        
        # Generate summary
        analysis['summary'] = {
            'total_files_changed': len(analysis['dependency_files_changed']),
            'total_dependencies_added': len(analysis['added_dependencies']),
            'total_dependencies_removed': len(analysis['removed_dependencies']),
            'total_dependencies_updated': len(analysis['updated_dependencies']),
            'security_alerts_count': len(analysis['security_alerts']),
            'major_updates_count': len([d for d in analysis['updated_dependencies'] if d.get('change_type') == 'major'])
        }
        
        # Add high-level suggestions based on summary
        if analysis['summary']['major_updates_count'] > 0:
            analysis['suggestions'].append({
                'suggestion': f'Multiple major version updates detected ({analysis["summary"]["major_updates_count"]}). Consider splitting into separate PRs for easier review.',
                'severity': 'info'
            })
        
        if analysis['summary']['security_alerts_count'] > 0:
            analysis['suggestions'].append({
                'suggestion': 'Security alerts detected. Review each alert and ensure dependencies are from trusted sources.',
                'severity': 'warning'
            })
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing dependencies: {e}")
        return {}

def format_review_comment(review_type: str, content: Union[str, Dict]) -> str:
    """Formats a review section for GitHub comment."""
    if isinstance(content, dict):
        if review_type == 'security':
            return format_security_review(content)
        return json.dumps(content, indent=2)
    return str(content)

def format_security_review(security_review: Dict) -> str:
    """Formats security review findings for GitHub comment."""
    output = []
    
    if security_review.get('vulnerabilities'):
        output.append("### 🔒 Security Vulnerabilities\n")
        for vuln in security_review['vulnerabilities']:
            output.append(f"- **{vuln['severity']}**: {vuln['description']}")
            output.append(f"  - File: `{vuln['file']}` Line: {vuln['line']}\n")
    
    if security_review.get('recommendations'):
        output.append("### 📋 Recommendations\n")
        for rec in security_review['recommendations']:
            output.append(f"#### {rec['title']} ({rec['priority']})")
            output.append(f"{rec['description']}\n")
            for item in rec['items']:
                output.append(f"- {item}")
            output.append("")
    
    return "\n".join(output)