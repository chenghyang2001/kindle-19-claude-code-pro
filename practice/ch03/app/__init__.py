"""Flask 應用程式工廠：建立 app 並註冊路由。"""

from flask import Flask


def create_app(config: dict | None = None) -> Flask:
    """建立 Flask app；config 用於測試時覆寫設定（例如 TESTING=True）。"""
    app = Flask(__name__)
    app.config.from_mapping(DATABASE_URL="sqlite:///dev.db")
    if config is not None:
        app.config.update(config)

    from app.routes import bp

    app.register_blueprint(bp)
    return app
