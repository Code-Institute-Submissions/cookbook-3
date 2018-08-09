from bson.objectid import ObjectId


# Related to AddRecipe class / Generate to SON object
def convert_to_son_obj(db):
    list = []
    
    for key in db["names"]:
        list.append((key, db["names"][key]))
    
    return list    
    
    
# Like and Dislike actions
def value_in_list(value, list):
    if value in list:
        boolean = True
    else:
        boolean = False
    return boolean
    
def update_author_data_liked_recipe(data, author_id, operator, value):
    data.update({"_id": ObjectId(author_id)},
                    {
                       operator: {"liked_recipe": value}
                    })

def update_author_data_disliked_recipe(data, author_id, operator, value):
    data.update({"_id": ObjectId(author_id)},
                    {
                       operator: {"disliked_recipe": value}
                    })