class users():
    def __init__(self) -> None:
        self.__users = {
            "name" : "user_id",
            "name" : "user_id",
            "name" : "user_id",
        }
    
    # Single getter
    def get_user(self,name:str) -> str:
        user = self.__users[name]
        return user

    # All getter
    def get_users(self):
        return self.__users.values()
        