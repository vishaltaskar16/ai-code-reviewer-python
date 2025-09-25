import openai
import os
from config import Config
import re

class CodeAnalyzer:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def analyze_code(self, code, language, review_type):
        """Analyze code for specific review type"""
        prompts = {
            'security': self._get_security_prompt(language),
            'quality': self._get_quality_prompt(language),
            'performance': self._get_performance_prompt(language)
        }
        
        prompt = prompts.get(review_type, self._get_quality_prompt(language))
        full_prompt = f"{prompt}\n\nCode:\n```{language}\n{code}\n```"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer. Provide specific, actionable feedback."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            return self._parse_response(response.choices[0].message.content, review_type)
            
        except Exception as e:
            return {'error': str(e), 'findings': []}
    
    def _get_security_prompt(self, language):
        return f"""Analyze this {language} code for security vulnerabilities. Focus on:
- Injection vulnerabilities (SQL, command, etc.)
- Authentication and authorization issues
- Data exposure risks
- Input validation problems
- Security misconfigurations
- Cryptographic weaknesses

Provide specific findings with:
1. Severity level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
2. Description of the issue
3. Specific suggestion for fixing
4. File path and line number if applicable

Format each finding as:
SEVERITY: Description
Suggestion: Fix suggestion
File: path:line"""

    def _get_quality_prompt(self, language):
        return f"""Review this {language} code for quality and best practices. Check:
- Code readability and structure
- Maintainability issues
- Code smells and anti-patterns
- Documentation and comments
- Error handling
- Code duplication
- Naming conventions

Provide specific findings with severity levels and suggestions."""

    def _get_performance_prompt(self, language):
        return f"""Analyze this {language} code for performance issues. Check:
- Algorithm efficiency
- Memory usage patterns
- Database query optimization
- Network call efficiency
- Caching opportunities
- Resource leaks

Provide specific performance recommendations with expected impact."""

    def _parse_response(self, response, review_type):
        """Parse AI response into structured data"""
        lines = response.split('\n')
        findings = []
        current_finding = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_finding:
                    findings.append(current_finding)
                    current_finding = {}
                continue
                
            if line.upper().startswith(('CRITICAL:', 'HIGH:', 'MEDIUM:', 'LOW:', 'INFO:')):
                if current_finding:
                    findings.append(current_finding)
                severity = line.split(':')[0].upper()
                description = ':'.join(line.split(':')[1:]).strip()
                current_finding = {'severity': severity, 'description': description}
                
            elif line.lower().startswith('suggestion:') and current_finding:
                current_finding['suggestion'] = line.split(':', 1)[1].strip()
                
            elif line.lower().startswith('file:') and current_finding:
                file_info = line.split(':', 1)[1].strip()
                if ':' in file_info:
                    path, line_num = file_info.rsplit(':', 1)
                    current_finding['file_path'] = path.strip()
                    try:
                        current_finding['line_number'] = int(line_num.strip())
                    except ValueError:
                        pass
        
        if current_finding:
            findings.append(current_finding)
        
        # Calculate score based on findings
        score = self._calculate_score(findings)
        
        return {
            'summary': response[:200] + '...' if len(response) > 200 else response,
            'findings': findings,
            'score': score
        }
    
    def _calculate_score(self, findings):
        """Calculate quality score based on findings"""
        base_score = 100
        severity_weights = {
            'CRITICAL': -20,
            'HIGH': -10,
            'MEDIUM': -5,
            'LOW': -2,
            'INFO': 0
        }
        
        for finding in findings:
            base_score += severity_weights.get(finding.get('severity', 'INFO'), 0)
        
        return max(0, min(100, base_score))

def analyze_code(code, language, review_types):
    """Main function to analyze code with multiple review types"""
    analyzer = CodeAnalyzer()
    results = {}
    
    for review_type in review_types:
        results[review_type] = analyzer.analyze_code(code, language, review_type)
    
    return results