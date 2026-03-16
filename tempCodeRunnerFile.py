
app = Flask(__name__)

# Ensure DB is initialized
database.init_db()
# Ensure model is ready (try loading)
classifier = analysis.ActivityClassifier()

@app.route('/')
def index():