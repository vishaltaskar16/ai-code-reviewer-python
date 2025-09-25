import requests
import os
import re
from config import Config
from services.ai_service import analyze_code

def analyze_github_pr(repo_url, pr_number):
    """Analyze GitHub pull request"""
    try:
        # Extract owner and repo from URL
        match = re.match(r'https://github.com/([^/]+)/([^/]+)', repo_url)
        if not match:
            return {'error': 'Invalid GitHub repository URL'}
        
        owner, repo = match.groups()
        
        # Get PR diff
        diff = get_pr_diff(owner, repo, pr_number)
        if not diff:
            return {'error': 'Could not fetch PR diff'}
        
        # Parse diff and analyze files
        files = parse_diff(diff)
        results = {}
        
        for file in files:
            if should_analyze_file(file['path']):
                file_results = analyze_code(file['content'], get_language(file['path']), ['security', 'quality'])
                results[file['path']] = file_results
        
        return results
        
    except Exception as e:
        return {'error': str(e)}

def get_pr_diff(owner, repo, pr_number):
    """Fetch PR diff from GitHub API"""
    token = Config.GITHUB_TOKEN
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3.diff'
    }
    
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"GitHub API error: {e}")
        return None

def parse_diff(diff_text):
    """Parse git diff into individual files"""
    files = []
    file_sections = diff_text.split('diff --git ')[1:]
    
    for section in file_sections:
        lines = section.split('\n')
        if not lines:
            continue
            
        # Extract filename
        file_line = lines[0]
        file_match = re.search(r'b/(.+)', file_line)
        if not file_match:
            continue
            
        filename = file_match.group(1)
        
        # Extract added lines
        content_lines = []
        for line in lines[1:]:
            if line.startswith('+') and not line.startswith('+++'):
                content_lines.append(line[1:])
        
        if content_lines:
            files.append({
                'path': filename,
                'content': '\n'.join(content_lines)
            })
    
    return files

def should_analyze_file(filename):
    """Check if file should be analyzed"""
    skip_extensions = ['.md', '.txt', '.json', '.yml', '.yaml', '.xml', '.csv']
    extension = '.' + filename.split('.')[-1] if '.' in filename else ''
    return extension not in skip_extensions

def get_language(filename):
    """Determine language from filename"""
    extensions = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'c++',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.html': 'html',
        '.css': 'css'
    }
    extension = '.' + filename.split('.')[-1] if '.' in filename else ''
    return extensions.get(extension, 'python')