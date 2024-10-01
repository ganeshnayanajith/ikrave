from marshmallow import Schema, fields, validate


class GetRecommendationsByFoodNameSchema(Schema):
    food_name = fields.Str(required=True, validate=validate.Length(min=1))
