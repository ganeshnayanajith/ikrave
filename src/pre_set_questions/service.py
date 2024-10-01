from libs.db import connect_to_mongodb


class PreSetQuestionService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.pre_set_questions_collection = self.db.pre_set_questions

    def get_pre_set_questions(self):
        cursor = self.pre_set_questions_collection.find()
        documents = []
        for document in cursor:
            document['_id'] = str(document['_id'])
            documents.append(document)
        print(f'get_pre_set_questions - success : {documents}')
        return documents
