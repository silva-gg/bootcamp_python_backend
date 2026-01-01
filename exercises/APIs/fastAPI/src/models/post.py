import sqlalchemy as sqa
from database import metadata
posts = sqa.Table(
    'posts',
    metadata,
    sqa.Column('id', sqa.Integer, primary_key=True),
    sqa.Column('title', sqa.String(150), nullable=False, unique=True),
    sqa.Column('publication_date', sqa.DateTime, nullable=False),
    sqa.Column('content', sqa.Text, nullable=False),
    sqa.Column('active', sqa.Boolean, default=True, nullable=False)
    )
