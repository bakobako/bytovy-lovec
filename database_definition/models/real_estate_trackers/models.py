from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from database_definition.models.base import Base

class Tracker(Base):
    __tablename__ = 'trackers'
    __table_args__ = {'schema': 'real_estate_trackers'}

    tracker_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('sales.customers.customer_id'), nullable=False)  # Linking to customers in sales schema
    tracker_name = Column(String, nullable=False)
    property_type = Column(String, nullable=True)
    min_price = Column(DECIMAL(15, 2), nullable=True)
    max_price = Column(DECIMAL(15, 2), nullable=True)
    min_bedrooms = Column(Integer, nullable=True)
    max_bedrooms = Column(Integer, nullable=True)
    min_square_meters = Column(DECIMAL(10, 2), nullable=True)
    max_square_meters = Column(DECIMAL(10, 2), nullable=True)
    preferences = Column(JSONB, nullable=True)  # Using JSONB for flexible preferences data
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)

    # Relationship to tracker_matches
    matches = relationship('TrackerMatch', backref='tracker', lazy='dynamic')

class TrackerMatch(Base):
    __tablename__ = 'tracker_matches'
    __table_args__ = {'schema': 'real_estate_trackers'}

    match_id = Column(Integer, primary_key=True)
    tracker_id = Column(Integer, ForeignKey('real_estate_trackers.trackers.tracker_id'), nullable=False)
    listing_id = Column(Integer, ForeignKey('real_estate_listings.analysed_real_estate_listings.listing_id'), nullable=False)  # Linking to listings in real_estate_listings schema

    # Relationship to tracker_notifications
    notifications = relationship('TrackerNotification', backref='tracker_match', lazy='dynamic')

class TrackerNotification(Base):
    __tablename__ = 'tracker_notifications'
    __table_args__ = {'schema': 'real_estate_trackers'}

    notification_id = Column(Integer, primary_key=True)
    tracker_match_id = Column(Integer, ForeignKey('real_estate_trackers.tracker_matches.match_id'), nullable=False)
    notification_method = Column(String, nullable=False)  # e.g., email, SMS, push notification
    sent_at = Column(TIMESTAMP, nullable=False)

