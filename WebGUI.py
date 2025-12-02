from flask import Flask, render_template, request, jsonify, Response, send_file
from multiprocessing import Process, freeze_support, Manager



import indexer
import text
import authentication
import os

app = Flask(__name__)

process = None

app.add_url_rule("/login", "login", authentication.login, methods = ["GET", "POST"])
app.add_url_rule("/logout", "logout", authentication.logout)
app.secret_key = os.urandom(24) 

@app.route("/")
@authentication.login_required
def index():
    return render_template("index.html")


@app.route("/index_database", methods=["POST"])
def index_database():
    global process
    if process is not None and not process.is_alive():
        process = None  # очистка
    def run_indexing():
        global process
        process = Process(target=indexer.index_local_pdfs, args=(progress_queue,))
        process.start()
    if not process:
        run_indexing()
        return jsonify({"status":"started"})
    return jsonify({"status" : "running"})


@app.route("/start_search", methods=["POST"])
def start_search():
    global process
    query = (request.form.get("query") or " ").strip()
    if query:
        accuracy = int(request.form.get("accuracy", 100))
        search_type = request.form.get("search_type")
        process = Process(target=text.search_by_query_json, args=(query, accuracy, search_type, results_queue, progress_queue))
        process.start()
        return jsonify({"status": "started"})
    return jsonify({"status":"error"})


@app.route("/upload_query", methods=["POST"])
def upload_file():
    file = request.files["query_file"]
    if file.filename and file.filename.endswith(".txt"):
        global process
        accuracy = int(request.form.get("accuracy", 100))
        process = Process(target=text.search_by_file, args=(file.read(), accuracy, results_queue, progress_queue))
        process.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "error"})


@app.route("/stream_next")
def stream_next():
    results = []
    while not results_queue.empty():
        batch = results_queue.get_nowait()
        results.extend(batch)  # flatten all batches into one list
    if results:
        return jsonify(results)
    return Response(status=204)

@app.route("/progress")
def get_progress():
    progress = []
    while not progress_queue.empty():
        progress.append(progress_queue.get())
    return jsonify(progress)


@app.route("/view_pdf")
def view_pdf():
    path = request.args.get("path")
    return send_file(path, mimetype="application/pdf")


if __name__ == "__main__":
    freeze_support()
    
    manager = Manager()
    progress_queue = manager.Queue()
    results_queue = manager.Queue()
    app.run(host="0.0.0.0", port=8000, debug=True)
