from marshmallow import Schema, fields


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    theme_id = fields.Int(required=True)
    title = fields.Str(required=True)
    answers = fields.Nested(AnswerSchema, required=True, many=True)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, required=True, many=True)


class ThemeIdSchema(Schema):
    id = fields.Int(required=False)


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, required=True, many=True)