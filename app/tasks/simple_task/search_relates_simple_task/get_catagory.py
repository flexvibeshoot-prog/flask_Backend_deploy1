from app.models import Category

def get_category_with_children(category_id, max_depth=3):
    root = Category.query.filter_by(category_id=category_id).first()
    if not root:
        return []

    result = [root.name]
    queue = [(root.category_id, 0)]  # (category_id, depth)

    while queue:
        current_id, depth = queue.pop(0)

        if depth >= max_depth:
            continue

        children = Category.query.filter_by(parent_id=current_id).all()
        for child in children:
            result.append(child.name)
            queue.append((child.category_id, depth + 1))

    return result

