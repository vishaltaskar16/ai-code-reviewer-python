import re

class SecurityScanner:
    """Basic security pattern scanner"""
    
    # Common vulnerability patterns
    PATTERNS = {
        'sql_injection': [
            r"execute\(.*\+.*\)",
            r"executescript\(.*\+.*\)",
            r"query\(.*['\"].*\+.*\)"
        ],
        'command_injection': [
            r"os\.system\(.*\+.*\)",
            r"subprocess\.call\(.*\+.*\)",
            r"eval\(.*\)"
        ],
        'hardcoded_secrets': [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]"
        ],
        'xss_vulnerabilities': [
            r"innerHTML\s*=\s*.+",
            r"document\.write\(.*\)"
        ]
    }
    
    def scan(self, code, language):
        """Basic security scan using pattern matching"""
        findings = []
        
        for vuln_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        'severity': 'HIGH',
                        'description': f'Potential {vuln_type.replace("_", " ")} detected',
                        'suggestion': f'Review this pattern for security issues: {match.group(0)}',
                        'type': vuln_type
                    })
        
        return findings