import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from libs.db import connect_to_mongodb
from libs.helpers import CustomException, ErrorTypesEnum, convert_object_ids_to_strings

from src.food.service import FoodService
from src.merchant.service import MerchantService
from src.user.service import UserService

food_service = FoodService()
user_service = UserService()
merchant_service = MerchantService()


class FoodRecommendationEngineService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.foods_cosine_sim_df_collection = self.db.foods_cosine_sim_df

    def get_recommendations_by_food_name(self, food_name: str, merchant_id=None):

        try:

            print(f"get_recommendations_by_food_name - food name : {food_name}")

            if merchant_id is None:
                foods = food_service.get_all_food_items()
            else:
                foods = food_service.get_food_items(merchant_id)

            if len(foods) == 0:
                print(f'get_recommendations_by_food_name - no food data in the database')
                raise CustomException(500, "Food database is empty", ErrorTypesEnum.INTERNAL_SERVER_ERROR.value)

            df = pd.DataFrame(foods)

            print(f"get_recommendations_by_food_name - food data frame : {df}")

            df['item_name_lower'] = df['item_name'].str.lower()

            count = CountVectorizer(stop_words='english')
            count_matrix = count.fit_transform(df['item_name_lower'])

            cosine_sim = cosine_similarity(count_matrix, count_matrix)

            cosine_sim_df = pd.DataFrame(cosine_sim)

            food_name_lower = food_name.lower()

            # a = df.reset_index(drop=True)
            a = df.copy().reset_index().drop('index', axis=1)

            index = a[a['item_name_lower'] == food_name_lower].index[0]

            top_n_index = list(cosine_sim_df[index].nlargest(10).index)

            top_n_index.remove(index)

            result = []

            for idx in top_n_index:
                food_object = {
                    "food_id": str(a.iloc[idx]['_id']),
                    "item_name": a.iloc[idx]['item_name'],
                    "cuisine_type": a.iloc[idx]['cuisine_type'],
                    "merchant_id": a.iloc[idx]['merchant_id'],
                    # "cosine_similarity": cosine_sim_df[index].iloc[idx]
                }
                result.append(food_object)

            print(f"get_recommendations_by_food_name - result : {result}")
            return result

        except IndexError as e:
            print(f"get_recommendations_by_food_name - no matching item found for: {food_name}")
            print(f"get_recommendations_by_food_name - error: {str(e)}")
            return []
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"get_recommendations_by_food_name - error - {str(e)}")
            raise CustomException(500, "Recommendation engine error", ErrorTypesEnum.INTERNAL_SERVER_ERROR.value)

    def get_recommendations_by_cuisine_type(self, cuisine_type: str, merchant_id=None):

        try:

            print(f"get_recommendations_by_cuisine_type - cuisine_type : {cuisine_type}")

            if merchant_id is None:
                foods = food_service.get_all_food_items()
            else:
                foods = food_service.get_food_items(merchant_id)

            if len(foods) == 0:
                print(f'get_recommendations_by_cuisine_type - no food data in the database')
                raise CustomException(500, "Food database is empty", ErrorTypesEnum.INTERNAL_SERVER_ERROR.value)

            df = pd.DataFrame(foods)

            print(f"get_recommendations_by_cuisine_type - food data frame : {df}")

            df['cuisine_type_lower'] = df['cuisine_type'].str.lower()

            count = CountVectorizer(stop_words='english')
            count_matrix = count.fit_transform(df['cuisine_type_lower'])

            cosine_sim = cosine_similarity(count_matrix, count_matrix)

            cosine_sim_df = pd.DataFrame(cosine_sim)

            cuisine_type_lower = cuisine_type.lower()

            # a = df.reset_index(drop=True)
            a = df.copy().reset_index().drop('index', axis=1)

            index = a[a['cuisine_type_lower'] == cuisine_type_lower].index[0]

            top_n_index = list(cosine_sim_df[index].nlargest(10).index)

            top_n_index.remove(index)

            result = []

            for idx in top_n_index:
                food_object = {
                    "food_id": str(a.iloc[idx]['_id']),
                    "item_name": a.iloc[idx]['item_name'],
                    "cuisine_type": a.iloc[idx]['cuisine_type'],
                    "merchant_id": a.iloc[idx]['merchant_id'],
                    # "cosine_similarity": cosine_sim_df[index].iloc[idx]
                }
                result.append(food_object)

            print(f"get_recommendations_by_cuisine_type - result : {result}")
            return result

        except IndexError as e:
            print(f"get_recommendations_by_cuisine_type - no matching item found for: {cuisine_type}")
            print(f"get_recommendations_by_cuisine_type - error: {str(e)}")
            return []
        except CustomException as e:
            raise e
        except Exception as e:
            print(f"get_recommendations_by_cuisine_type - error - {str(e)}")
            raise CustomException(500, "Recommendation engine error", ErrorTypesEnum.INTERNAL_SERVER_ERROR.value)

    def get_recommendations_for_user(self, user_id: str, merchant_id: str):

        food_names = user_service.get_user_favorite_foods(user_id)
        cuisine_types = user_service.get_user_favorite_cuisine_types(user_id)

        recommendations_by_food_names = []
        recommendations_by_cuisine_types = []

        for food_name in food_names:
            recommendations_by_food_names.extend(self.get_recommendations_by_food_name(food_name, merchant_id)[:3])

        for cuisine_type in cuisine_types:
            recommendations_by_cuisine_types.extend(
                self.get_recommendations_by_cuisine_type(cuisine_type, merchant_id)[:3])

        for item in recommendations_by_food_names:
            food = food_service.get_food_item_by_food_id(item['food_id'])
            item['food_data'] = convert_object_ids_to_strings(food)

            merchant = merchant_service.get_merchant(item['merchant_id'])
            item['merchant_data'] = convert_object_ids_to_strings(merchant)

        for item in recommendations_by_cuisine_types:
            food = food_service.get_food_item_by_food_id(item['food_id'])
            item['food_data'] = convert_object_ids_to_strings(food)

            merchant = merchant_service.get_merchant(item['merchant_id'])
            item['merchant_data'] = convert_object_ids_to_strings(merchant)

        print(f"get_recommendations_for_user - recommendations_by_food_names : {recommendations_by_food_names}")
        print(f"get_recommendations_for_user - recommendations_by_cuisine_types : {recommendations_by_cuisine_types}")
        return {
            'recommendations_by_food_names': recommendations_by_food_names,
            'recommendations_by_cuisine_types': recommendations_by_cuisine_types,
        }
