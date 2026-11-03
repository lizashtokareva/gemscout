from models import Base, Gem
from database import engine

Base.metadata.create_all(bind=engine)

