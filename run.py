from app import create_app
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        use_reloader=False)
