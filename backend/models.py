# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email_list = Column(JSON)  # 存储邮箱列表
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 添加反向关系
    subscriptions = relationship("Subscription", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    search_params = Column(JSON)
    search_url = Column(String)
    email_list = Column(JSON)  # 添加 email_list 字段
    status = Column(Boolean, default=True)  # 订阅状态
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 添加关系
    user = relationship("User", back_populates="subscriptions")
    logs = relationship("Log", back_populates="subscription", cascade="all, delete-orphan")

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    job_key = Column(String)  # 职位缓存key
    email_title = Column(String)
    email_content = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    # 添加反向关系
    subscription = relationship("Subscription", back_populates="logs") 