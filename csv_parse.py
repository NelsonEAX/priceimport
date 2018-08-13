import csv
from datetime import datetime

csv_file = 'analyze/opencart_csv-price-pro-importexport-4.csv'

class Attribute:
    """Атрибуты и связи"""

    def __init__(self):
        """Constructor"""
        pass

class Category:
    """Категории"""

    def __init__(self, name, date, id, parent = 0):
        """Constructor"""
        self.category_id = id
        self.name = name # obj["_CATEGORY_"]
        self.image = None
        self.parent_id = parent
        self.top = 1 # По умолчанию считаем родительской категорией
        self.column = 1 # ?
        self.status = 1 # По умолчанию включено
        self.date_added = date # По умолчанию текущая дата
        self.date_modified = date # По умолчанию текущая дата
        self.store_id = 0  # По умолчанию id магазина 0

    def __eq__(self, other):
        """Сравниваем по названию производителя"""
        return self.name == other.name and self.parent == other.parent

    def __hash__(self):
        """Для hashable"""
        return hash(self.name)

class Manufacturer(object):
    """Производи"""

    def __init__(self, obj):
        """Constructor"""
        self.manufacturer_id = None
        self.name = obj["_MANUFACTURER_"]
        self.image = None
        self.sort_order = 0 #По умолчанию без сортировки
        self.store_id = 0 #По умолчанию id магазина 0

    def __eq__(self, other):
        """Сравниваем по названию производителя"""
        return self.name == other.name

    def __hash__(self):
        """Для hashable"""
        return hash(self.name)

class Option:
    """Опции"""

    def __init__(self):
        """Constructor"""
        pass

class Product:
    """Продукция"""

    def __init__(self):
        """Constructor"""
        pass

class ProductOption:
    """Опции продукции"""

    def __init__(self):
        """Constructor"""
        pass


class CSVImport:
    """Класс генерации sql-файла ипорта прайса от Поставщика Счастья из csv"""

    def __init__(self, file):
        """Constructor"""
        self.file = file
        self.date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # self.attribute = Attribute()
        # self.Category = Category()
        # self.Manufacturer = Manufacturer()
        # self.Option = Option()
        # self.Product = Product()
        # self.ProductOption = ProductOption()

        self.attribute = set()
        self.category = dict()
        self.categories_id = set()
        self.manufacturer = set()
        self.option = set()
        self.product = set()
        self.prodoption = set()

        with open(self.file, 'r', encoding='utf-8') as f_obj:
            self.csv_reader(f_obj)

    def csv_reader(self, file_obj):
        """
        Read a CSV file using csv.DictReader
        """
        reader = csv.DictReader(file_obj, delimiter=';')
        for csv_line in reader:
            # Производители
#            self.manufacturer.add(Manufacturer(csv_line))

            # Несколько категорий
            self.categories_id.clear()
            multiple_cat_list = csv_line["_CATEGORY_"].split("\n")
            for single_cat_list in multiple_cat_list:
                # Категории
                parent = 0
                cat_list = single_cat_list.split("|")

                for category in cat_list:
                    new_cat_obj = Category(name=category, date=self.date, id=len(self.category)+1, parent=parent)

                    cat_obj = self.category.get(category)
                    if cat_obj is None:
                        self.category[category] = new_cat_obj
                        parent = new_cat_obj.category_id
                    else:
                        parent = cat_obj.category_id

                # Последний id в группе и есть id товара. Может быть несколько
                self.categories_id.add(parent)

            print(str(self.categories_id))




        # for manuf in self.manufacturer:
        #     print(manuf.name)

        for key in self.category:
            cat = self.category[key]
            print(str(cat.category_id) + '\t' + str(cat.parent_id) + '\t' + cat.name)



if __name__ == "__main__":

    csvimport = CSVImport(csv_file)
    csvimport.create_attribute_sql()
    csvimport.create_category_sql()
    csvimport.create_manufacturer_sql()
    csvimport.create_option_sql()
    csvimport.create_product_sql()
    csvimport.create_product_option_sql()













