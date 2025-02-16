from app import create_app

app = create_app()

if __name__ == "__main__":
    # Listen on all network interfaces, port 5000 by default
    app.run(host='0.0.0.0', port=5000, debug=True)
