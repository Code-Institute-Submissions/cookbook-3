import unittest
from utils import value_in_list, convert_to_son_obj

class TestApp(unittest.TestCase):
    
    
    def test_value_in_list(self):
        value = "str2"
        list = ["str1", "str2", "str3"]
        
        self.assertTrue(value_in_list(value, list))
        
    
    def test_convert_to_son_obj(self):
        dataB = {"names": {
                    "thai": "Thai",
                    "indian": "Indian"
                }}
        son = [("thai", "Thai"), ("indian", "Indian")]
        self.assertEqual(convert_to_son_obj(dataB), son)

if __name__ == "__main__":
    unittest.main()