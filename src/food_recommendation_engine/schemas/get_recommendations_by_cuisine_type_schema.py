from marshmallow import Schema, fields, validate


class GetRecommendationsByCuisineTypeSchema(Schema):
    cuisine_type = fields.Str(required=True, validate=validate.Length(min=1))
