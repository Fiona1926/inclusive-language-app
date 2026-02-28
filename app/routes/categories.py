"""
Categories and levels with unlock status.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.models import Category, Level, UserLevelProgress

categories_bp = Blueprint("categories", __name__)


def _user_progress_map(user_id):
    rows = UserLevelProgress.query.filter_by(user_id=user_id).all()
    return {p.level_id: p for p in rows}


@categories_bp.route("", methods=["GET"])
@categories_bp.route("/", methods=["GET"])
def list_categories():
    categories = Category.query.order_by(Category.order).all()
    out = []
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
    except Exception:
        pass

    progress_map = _user_progress_map(user_id) if user_id else {}
    for c in categories:
        levels = Level.query.filter_by(category_id=c.id).order_by(Level.order).all()
        level_list = []
        for l in levels:
            p = progress_map.get(l.id)
            level_list.append({
                "id": l.id,
                "order": l.order,
                "name": l.name,
                "description": l.description,
                "completed": p.completed if p else False,
                "completedAt": p.completed_at.isoformat() if p and p.completed_at else None,
            })
        out.append({
            "id": c.id,
            "slug": c.slug,
            "name": c.name,
            "description": c.description,
            "order": c.order,
            "levels": level_list,
        })
    return jsonify(out)


@categories_bp.route("/<category_slug>/levels", methods=["GET"])
def category_levels(category_slug):
    category = Category.query.filter_by(slug=category_slug).first()
    if not category:
        return jsonify({"error": "Category not found"}), 404

    levels = Level.query.filter_by(category_id=category.id).order_by(Level.order).all()
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
    except Exception:
        pass

    progress_map = _user_progress_map(user_id) if user_id else {}
    level_ids = [l.id for l in levels]
    out = []
    for i, level in enumerate(levels):
        prev_completed = True
        if i > 0:
            prev_p = progress_map.get(levels[i - 1].id)
            prev_completed = bool(prev_p and prev_p.completed)
        p = progress_map.get(level.id)
        out.append({
            **{k: getattr(level, k) for k in ["id", "order", "name", "description"]},
            "unlocked": prev_completed,
            "completed": p.completed if p else False,
            "completedAt": p.completed_at.isoformat() if p and p.completed_at else None,
        })
    return jsonify(out)
