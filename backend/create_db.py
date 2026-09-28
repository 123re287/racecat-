from database import Base, engine
from models import Project

Base.metadata.create_all(bind=engine)

print("🐱 赛程猫数据库创建成功！")