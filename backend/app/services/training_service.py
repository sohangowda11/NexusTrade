import logging
import os
import pickle
from datetime import datetime
from typing import Optional, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.models.orm_models import AnalysisSession, AIVote

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/ensemble_model.pkl")
MODEL_NAMES = ["Claude Sonnet", "GPT-4o", "Gemini 1.5 Pro", "DeepSeek Chat"]


def _build_row(session: AnalysisSession) -> list:
    """Convert one AnalysisSession into a flat feature vector."""
    votes_r2 = {v.model_name: v for v in session.votes if v.discussion_round == 2}
    if not votes_r2:
        votes_r2 = {v.model_name: v for v in session.votes}

    row = []
    directions = []
    for name in MODEL_NAMES:
        v = votes_r2.get(name)
        if v:
            dir_val = 1 if v.direction == "up" else 0
            risk_val = {"low": 0, "medium": 1, "high": 2}.get(v.risk_level, 1)
            row.extend([dir_val, v.confidence / 100.0, risk_val])
            directions.append(dir_val)
        else:
            row.extend([-1, 0.5, 1])
            directions.append(-1)

    valid = [d for d in directions if d != -1]
    if valid:
        majority = round(sum(valid) / len(valid))
        consensus = sum(1 for d in valid if d == majority) / len(valid)
    else:
        consensus = 0.0
    row.append(consensus)
    row.append(session.timestamp.weekday() / 6.0)
    row.append(session.timestamp.hour / 23.0)
    return row


def build_feature_matrix(db: Session) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    sessions = (
        db.query(AnalysisSession)
        .filter(AnalysisSession.price_24h_later.isnot(None))
        .all()
    )
    if not sessions:
        return None, None

    rows, labels = [], []
    for s in sessions:
        label = 1 if (
            (s.price_24h_later > s.price_at_analysis) == (s.final_direction == "up")
        ) else 0
        rows.append(_build_row(s))
        labels.append(label)

    return np.array(rows, dtype=float), np.array(labels, dtype=int)


def train_model(db: Session) -> dict:
    X, y = build_feature_matrix(db)

    if X is None or len(X) < 20:
        return {
            "status": "insufficient_data",
            "samples": int(len(X)) if X is not None else 0,
            "needed": 20,
        }

    try:
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import cross_val_score

        clf = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)
        clf.fit(X, y)
        cv_scores = cross_val_score(clf, X, y, cv=min(5, len(X) // 4), scoring="accuracy")

        feature_names = (
            [f"{m}_{f}" for m in MODEL_NAMES for f in ["dir", "conf", "risk"]]
            + ["consensus", "weekday", "hour"]
        )
        importances = dict(zip(feature_names, clf.feature_importances_.tolist()))

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump({
                "model": clf,
                "trained_at": datetime.utcnow().isoformat(),
                "accuracy": float(cv_scores.mean()),
                "samples": len(X),
                "feature_importances": importances,
            }, f)

        return {
            "status": "trained",
            "accuracy": round(float(cv_scores.mean()), 4),
            "cv_scores": cv_scores.tolist(),
            "feature_importances": importances,
            "samples_used": len(X),
        }
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return {"status": "error", "error": str(e)}


def get_training_status() -> dict:
    if not os.path.exists(MODEL_PATH):
        return {"model_exists": False, "last_trained": None, "accuracy": None, "samples_used": None}
    try:
        with open(MODEL_PATH, "rb") as f:
            meta = pickle.load(f)
        return {
            "model_exists": True,
            "last_trained": meta.get("trained_at"),
            "accuracy": meta.get("accuracy"),
            "samples_used": meta.get("samples"),
            "feature_importances": meta.get("feature_importances"),
        }
    except Exception:
        return {"model_exists": False, "last_trained": None, "accuracy": None, "samples_used": None}


def predict_enhanced(analysis_result: dict) -> Optional[dict]:
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        with open(MODEL_PATH, "rb") as f:
            meta = pickle.load(f)
        clf = meta["model"]
        votes_dict = {v["model_name"]: v for v in analysis_result.get("round2_votes", [])}
        row = []
        for name in MODEL_NAMES:
            v = votes_dict.get(name)
            if v:
                row.extend([1 if v["direction"] == "up" else 0, v["confidence"] / 100.0,
                             {"low": 0, "medium": 1, "high": 2}.get(v["risk_level"], 1)])
            else:
                row.extend([-1, 0.5, 1])
        row.extend([
            analysis_result.get("consensus_score", 50) / 100.0,
            datetime.utcnow().weekday() / 6.0,
            datetime.utcnow().hour / 23.0,
        ])
        prob = clf.predict_proba([row])[0]
        return {
            "ensemble_direction": "up" if prob[1] > 0.5 else "down",
            "ensemble_confidence": round(float(max(prob)) * 100, 1),
            "up_probability": round(float(prob[1]) * 100, 1),
        }
    except Exception as e:
        logger.warning(f"Enhanced prediction failed: {e}")
        return None
