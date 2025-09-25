from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config
import json
import time
from services.ai_service import analyze_code
from services.github_service import analyze_github_pr
from database.models import db, CodeReview, ReviewFinding
from utils.helpers import rate_limit

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ✅ Create tables at startup (Flask 3.x compatible)
with app.app_context():
    db.create_all()
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    """Main dashboard"""
    recent_reviews = CodeReview.query.order_by(CodeReview.created_at.desc()).limit(5).all()
    
    # Calculate stats
    total_reviews = CodeReview.query.count()
    avg_score = db.session.query(db.func.avg(CodeReview.score)).scalar() or 0
    critical_issues = ReviewFinding.query.filter_by(severity='CRITICAL').count()
    
    stats = {
        'total_reviews': total_reviews,
        'average_score': round(avg_score, 1),
        'critical_issues': critical_issues
    }
    
    return render_template('index.html', stats=stats, recent_reviews=recent_reviews)

@app.route('/review', methods=['GET', 'POST'])
def review():
    """Code review interface"""
    if request.method == 'POST':
        return handle_code_review(request)
    return render_template('review.html')

@app.route('/analyze', methods=['POST'])
@rate_limit(10, 60)  # 10 requests per minute
def analyze():
    """API endpoint for code analysis"""
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        code = data['code']
        language = data.get('language', 'python')
        review_types = data.get('review_types', ['security', 'quality', 'performance'])
        
        results = analyze_code(code, language, review_types)
        
        # Save to database
        review = CodeReview(
            code_snippet=code[:1000],  # Store first 1000 chars
            language=language,
            review_types=','.join(review_types),
            results=json.dumps(results),
            score=calculate_overall_score(results)
        )
        db.session.add(review)
        db.session.commit()
        
        # Save findings
        for review_type, result in results.items():
            if 'findings' in result:
                for finding in result['findings']:
                    review_finding = ReviewFinding(
                        review_id=review.id,
                        review_type=review_type,
                        severity=finding.get('severity', 'INFO'),
                        description=finding.get('description', ''),
                        suggestion=finding.get('suggestion', ''),
                        file_path=finding.get('file_path', ''),
                        line_number=finding.get('line_number')
                    )
                    db.session.add(review_finding)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'review_id': review.id,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    """Review history page"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    reviews = CodeReview.query.order_by(CodeReview.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('history.html', reviews=reviews)

@app.route('/review/<int:review_id>')
def review_details(review_id):
    """Individual review details"""
    review = CodeReview.query.get_or_404(review_id)
    findings = ReviewFinding.query.filter_by(review_id=review_id).all()
    
    return render_template('results.html', review=review, findings=findings)

@app.route('/github-review', methods=['POST'])
def github_review():
    """GitHub PR review endpoint"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        pr_number = data.get('pr_number')
        
        if not repo_url or not pr_number:
            return jsonify({'error': 'Repository URL and PR number are required'}), 400
        
        results = analyze_github_pr(repo_url, pr_number)
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_code_review(request):
    """Handle code review form submission"""
    code = request.form.get('code')
    language = request.form.get('language', 'python')
    review_types = request.form.getlist('review_types')
    
    if not code:
        return render_template('review.html', error='Please provide code to review')
    
    try:
        results = analyze_code(code, language, review_types)
        
        # Save to database
        review = CodeReview(
            code_snippet=code[:1000],
            language=language,
            review_types=','.join(review_types),
            results=json.dumps(results),
            score=calculate_overall_score(results)
        )
        db.session.add(review)
        db.session.commit()
        
        return redirect(url_for('review_details', review_id=review.id))
        
    except Exception as e:
        return render_template('review.html', error=str(e))

def calculate_overall_score(results):
    """Calculate overall score from all review types"""
    scores = []
    for result in results.values():
        if 'score' in result:
            scores.append(result['score'])
    return round(sum(scores) / len(scores)) if scores else 0

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # ensures tables exist
    app.run(debug=True, host='0.0.0.0', port=5000)
