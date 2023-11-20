from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()


class Station(db.Model):
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    city = db.Column(db.String(80))

    def __repr__(self):
        return f"<Station {self.name}>"

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise AssertionError("No station name provided")

        if len(name) < 3:
            raise AssertionError("Station name must be at least 3 characters long")

        if Station.query.filter(Station.name == name).first():
            raise AssertionError("Station name must be unique")

        return name


class Platform(db.Model):
    __tablename__ = "platforms"

    id = db.Column(db.Integer, primary_key=True)
    platform_num = db.Column(db.Integer)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"))

    def __repr__(self):
        return f"<Platform {self.name}>"

    @validates("platform_num")
    def validate_platform_num(self, key, platform_num):
        if not platform_num:
            raise AssertionError("No platform number provided")

        if not isinstance(platform_num, int):
            raise AssertionError("Platform number must be an integer")

        if platform_num < 1 or platform_num > 20:
            raise AssertionError("Platform number must be in the range 1-20")

        if Platform.query.filter(Platform.platform_num == platform_num).first():
            raise AssertionError("Platform number must be unique to each station")

        return platform_num


class Train(db.Model):
    __tablename__ = "trains"

    id = db.Column(db.Integer, primary_key=True)
    train_num = db.Column(db.String)
    service_type = db.Column(db.String)
    origin = db.Column(db.String)
    destination = db.Column(db.String)

    def __repr__(self):
        return f"<Train {self.name}>"

    @validates("origin")
    def validate_origin(self, key, origin):
        if not origin:
            raise AssertionError("No origin provided")

        if len(origin) < 3 or len(origin) > 24:
            raise AssertionError("Origin must be between 3 and 24 characters long")

        return origin

    @validates("destination")
    def validate_destination(self, key, destination):
        if not destination:
            raise AssertionError("No destination provided")

        if len(destination) < 3 or len(destination) > 24:
            raise AssertionError("Destination must be between 3 and 24 characters long")

        return destination

    @validates("service_type")
    def validate_service_type(self, key, service_type):
        if not service_type:
            raise AssertionError("No service type provided")

        if service_type != "express" and service_type != "local":
            raise AssertionError("Service type must be either 'express' or 'local'")

        return service_type


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    arrival_time = db.Column(db.DateTime)
    departure_time = db.Column(db.DateTime)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"))
    platform_id = db.Column(db.Integer, db.ForeignKey("platforms.id"))

    def __repr__(self):
        return f"<Assignment Train No: {self.train.train_num} Platform: {self.platform.platform_num}>"

    @validates("arrival_time")
    def validate_arrival_time(self, key, arrival_time):
        if not arrival_time:
            raise AssertionError("No arrival time provided")
        if not self.departure_time:
            raise AssertionError("No departure time provided")
        if arrival_time > self.departure_time:
            raise AssertionError("Arrival time must be before departure time")

        return arrival_time

    @validates("departure_time")
    def validate_departure_time(self, key, departure_time):
        if not departure_time:
            raise AssertionError("No departure time provided")
        if not self.arrival_time:
            raise AssertionError("No arrival time provided")
        if (departure_time - self.arrival_time).total_seconds() > 1200:
            raise AssertionError(
                "Train must not stay at platform for more than 20 minutes"
            )

        return departure_time

    @validates("platform_id")
    def validate_platform_id(self, key, platform_id):
        if not platform_id:
            raise AssertionError("No platform id provided")
        if not Platform.query.filter(Platform.id == platform_id).first():
            raise AssertionError("Platform id must be valid")
        if Assignment.query.filter(Assignment.platform_id == platform_id).first():
            raise AssertionError("Platform must be vacant")

        return platform_id
