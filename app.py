from flask import Flask, render_template, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import subprocess, json, os

try:
    import psutil
except ImportError:
    psutil = None

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'omni_godmode.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    links = db.Column(db.Integer, default=0)
    dr = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    backlinks = db.relationship('Backlink', backref='scan', lazy=True, cascade="all, delete-orphan")

class Backlink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan_result.id'), nullable=False)
    source_url = db.Column(db.String(1000))
    title = db.Column(db.String(500))
    anchor = db.Column(db.String(500))
    dr = db.Column(db.Integer)
    status = db.Column(db.String(50))
    category = db.Column(db.String(50))

with app.app_context():
    db.create_all()

@app.route('/seo/')
def index():
    return render_template('index.html')

@app.route('/seo/report/<domain>')
def view_report(domain):
    scan = ScanResult.query.filter_by(domain=domain).first_or_404()
    return render_template('report.html', scan=scan)

@app.route('/seo/recent', methods=['GET'])
def recent_scans():
    scans = ScanResult.query.order_by(ScanResult.date.desc()).limit(10).all()
    result = []
    for s in scans:
        result.append({
            "domain": s.domain,
            "links": s.links,
            "dr": s.dr,
            "date": s.date.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(result)

@app.route('/seo/analyze', methods=['POST'])
def analyze():
    target_url = request.form.get('url', '').strip()
    if not target_url: return "No URL", 400
    
    def generate():
        script = os.path.join(basedir, "live_backlinks.py")
        process = subprocess.Popen(["python3", "-u", script, target_url], 
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        final_dr = 0
        total_links = 0
        collected_links = []
        
        while True:
            line_raw = process.stdout.readline()
            if not line_raw and process.poll() is not None: break
            line = line_raw.decode('utf-8', errors='replace').strip()
            if not line: continue
            
            if "[METRIC_DR]" in line:
                try: final_dr = int(line.split("[METRIC_DR]")[1].strip())
                except: pass
            
            if "[LINK_DATA]" in line:
                total_links += 1
                try:
                    json_str = line.split("[LINK_DATA]")[1].strip()
                    link_data = json.loads(json_str)
                    collected_links.append(link_data)
                except: pass

            stats = {
                "cpu": psutil.cpu_percent() if psutil else 0,
                "ram": psutil.virtual_memory().percent if psutil else 0,
                "msg": line
            }
            yield f"data: {json.dumps(stats)}\n\n"
            
        process.wait()
        
        # Sla op in de database nadat het script klaar is
        with app.app_context():
            scan = ScanResult.query.filter_by(domain=target_url).first()
            if not scan:
                scan = ScanResult(domain=target_url)
                db.session.add(scan)
            else:
                # Verwijder oude links voor een frisse update
                Backlink.query.filter_by(scan_id=scan.id).delete()
                
            scan.links = total_links
            scan.dr = final_dr
            scan.date = datetime.utcnow()
            db.session.commit()
            
            # Bulk insert backlinks
            for ld in collected_links:
                new_link = Backlink(
                    scan_id=scan.id,
                    source_url=ld.get('source', ''),
                    title=ld.get('title', ''),
                    anchor=ld.get('anchor', ''),
                    dr=ld.get('link_dr', 0),
                    status=ld.get('status', ''),
                    category=ld.get('category', '')
                )
                db.session.add(new_link)
            db.session.commit()

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['X-Accel-Buffering'] = 'no'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)