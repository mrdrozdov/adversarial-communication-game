from pyramid.view import view_config

from ..models import FlickrQuerySet, FlickrQuery, Example, Label


@view_config(route_name='summary', renderer='../templates/summary.jinja2')
def summary(request):
    session = request.dbsession

    labels = session.query(Label).order_by(Label.name).all()
    label_dicts = {label.name: { "label": label } for label in labels}

    for label_name, _label in label_dicts.items():
        example_ids = set(ex.resource_id for ex in _label["label"].examples)
        _label["size"] = len(example_ids)

    return dict(label_dicts=label_dicts)
