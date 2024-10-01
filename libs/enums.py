from enum import Enum


class UserRolesEnum(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    MERCHANT = "MERCHANT"
    DRIVER = "DRIVER"


class MerchantRequestStatusEnum(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class OrderStatusEnum(Enum):
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY_TO_PICKUP = "READY_TO_PICKUP"
    PICKEDUP = "PICKEDUP"
    COMPLETED = "COMPLETED"


class OrderPaymentMethodEnum(Enum):
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"
    CARD_ON_DELIVERY = "CARD_ON_DELIVERY"


class DriverStatusEnum(Enum):
    WAITING = "WAITING"
    ASSIGNED = "ASSIGNED"


class CuisineTypeEnum(Enum):
    INDIAN = "INDIAN"
    CHINESE = "CHINESE"
    GREEK = "GREEK"
    ITALIAN = "ITALIAN"
    FRENCH = "FRENCH"
    BRITISH = "BRITISH"
    THAI = "THAI"
    ARABIC = "ARABIC"
    TURKISH = "TURKISH"
    OTHER_ASIAN = "OTHER_ASIAN"
    OTHER = "OTHER"


class ErrorTypesEnum(Enum):
    BAD_REQUEST_ERROR = "Bad Request Error"
    NOT_FOUND_ERROR = "Not Found Error"
    UNPROCESSABLE_ENTITY_ERROR = "Unprocessable Entity Error"
    INTERNAL_SERVER_ERROR = "Internal Server Error"
    FORBIDDEN_ERROR = "Forbidden Error"
    UNAUTHORIZED_ERROR = "Unauthorized Error"
