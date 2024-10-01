import db_seed_indexes
import db_seed_pre_set_questions
import db_seed_admins
import db_seed_users
import db_seed_merchants
import db_seed_foods


def seed_all():
    db_seed_indexes.seed()
    db_seed_pre_set_questions.seed()
    db_seed_admins.seed()
    db_seed_users.seed()
    db_seed_merchants.seed()
    db_seed_foods.seed()


if __name__ == "__main__":
    seed_all()
