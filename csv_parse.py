"""
autor: NelsonEAX
http://www.opencartlabs.ru/csv-price-pro-importexport-3/csvprice3-doc-csv/
http://www.opencartlabs.ru/csv-price-pro-importexport-3/import-opencart-options/
"""

import csv
from datetime import datetime
from string import Template

csv_file = 'analyze/opencart_csv-price-pro-importexport-4.csv'
sql_file = 'sql/result.sql'

class Attribute:
    """Атрибуты и связи"""

    def __init__(self, id, desc, attr, group_id, product_id):
        """Constructor"""
        self.id = id
        self.desc = desc
        self.attr = attr #oc_product_attribute.text
        self.group_id = group_id
        self.product_id = product_id

class AttributeGroup:
    """Группы атрибутов"""

    def __init__(self, id, desc):
        """Constructor"""
        self.id = id
        self.desc = desc

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

class Manufacturer:
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

    def __init__(self, id, type, desc, value ):
        """Constructor"""
        self.id = id
        self.type = type #oc_option radio/checkbox/text/select/textarea/file/date/time/datetime
        self.desc = desc #oc_option_description
        self.value = value # oc_option_value_description

class OptionValue:
    """ЗначенияОпций"""

    def __init__(self, product_id, option_id, obj):
        """Constructor"""
        self.product_id = product_id
        self.option_id = option_id
        self.quantity = obj[3]
        self.subtract = obj[4]
        self.price = obj[5]
        self.price_prefix = obj[6]
        self.points = obj[7]
        self.points_prefix = obj[8]
        self.weight = obj[9]
        self.weight_prefix = obj[10]

class Product:
    """Продукция"""

    def __init__(self, obj, imgs):
        """Constructor"""
        self.name = obj["_NAME_"]
        self.model = obj["_MODEL_"]
        self.sku = obj["_SKU_"]
        self.price = obj["_PRICE_"]
        self.quantity = obj["_QUANTITY_"]
        self.description = obj["_DESCRIPTION_"]
        self.name = obj["_WEIGHT_"]
        self.name = obj["_LENGTH_"]
        self.shipping = obj["_SHIPPING_"]
        self.subtract = obj["_subtract_"]
        self.html_h1 = obj["_HTML_H1_"]
        self.html_title = obj["_HTML_TITLE_"]
        self.special = obj["_SPECIAL_"]
        self.images = imgs

class ProductOption:
    """Опции продукции"""

    def __init__(self):
        """Constructor"""
        pass

class CSVImport:
    """Класс генерации sql-файла ипорта прайса от Поставщика Счастья из csv"""

    def __init__(self, csv_file, sql_file):
        """Constructor"""
        self.csv_file = csv_file
        self.sql_file = sql_file
        self.date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        self.attribute = list()
        self.attr_group = dict()
        self.category = dict()
        self.categories_id = set()
        self.manufacturer = set()
        self.option = dict()
        self.optionvalue = list()
        self.product = set()
        self.prodoption = set()
        self.product_id = None # Текущий товар, его id у поставщика

        with open(self.csv_file, 'r', encoding='utf-8') as f_obj:
            self.csv_reader(f_obj)

    def csv_reader(self, file_obj):
        """
        Read a CSV file using csv.DictReader
        """
        print('-------------sql_export-------------')
        reader = csv.DictReader(file_obj, delimiter=';')
        for csv_line in reader:
            # Продукция
            self.parse_product(csv_line)
            # Производители
            self.parse_manufacturer(csv_line)
            # Категории
            self.parse_category(csv_line)
            # Опции
            self.parse_option(csv_line)
            # Атрибуты
            self.parse_attribute(csv_line)

            # print(str(self.product_id)) ###

        # Производители ###
        # for manuf in self.manufacturer:
        #     print(manuf.name)

        # Категории ###
        # for key in self.category:
        #     cat = self.category[key]
        #     print(str(cat.category_id) + '\t' + str(cat.parent_id) + '\t' + cat.name)

        # Производители ###
        # for item in self.optionvalue:
        #     print(str(item))

        # Аттрибуты ###
        # for item in self.attribute:
        #     print(str(item.desc) + '\t' + str(item.attr))

    def parse_product(self, csv_line):
        """Парсинг продукции"""
        # Изображения забиваем в словарь. Ключ позже станет сортировкой
        imgs = dict() #
        for img in csv_line["_IMAGE_"].split(','):
            if img in (''):
                continue
            imgs[img] = len(imgs)

        for img in csv_line["_IMAGES_"].split(','):
            if img in (''):
                continue
            imgs[img] = len(imgs)

        # Инициируем обьект
        self.product.add(Product(csv_line, imgs))
        self.product_id = csv_line["_SKU_"]

    def parse_manufacturer(self, csv_line):
        """Парсинг производителей"""
        self.manufacturer.add(Manufacturer(csv_line))

    def parse_category(self, csv_line):
        """Парсинг категорий"""
        # Несколько категорий
        self.categories_id.clear()
        multiple_cat_list = csv_line["_CATEGORY_"].split("\n")
        for single_cat_list in multiple_cat_list:
            # Категории
            parent = 0
            cat_list = single_cat_list.split("|")

            for category in cat_list:
                new_cat_obj = Category(name=category, date=self.date, id=len(self.category) + 1, parent=parent)

                cat_obj = self.category.get(category)
                if cat_obj is None:
                    self.category[category] = new_cat_obj
                    parent = new_cat_obj.category_id
                else:
                    parent = cat_obj.category_id

            # Последний id в группе и есть id товара. Может быть несколько
            self.categories_id.add(parent)

        # print(str(self.categories_id))###

    def parse_option(self, csv_line):
        """Парсинг производителей"""
        multiple_opt_list = csv_line["_OPTIONS_"].split("\n")
        for single_opt_list in multiple_opt_list:
            # Опции
            if single_opt_list in (''):
                continue

            opt_list = single_opt_list.split("|")

            opt_type = opt_list[0]
            opt_descs = opt_list[1].split('/')
            opt_values = opt_list[2].split('/')

            opt_id_list = list() # лист id опций текущего товара

            for id, opt_desc in enumerate(opt_descs):

                if id > len(opt_values)-1:
                    continue

                new_opt_obj = Option(id=len(self.option) + 1, type=opt_type, desc=opt_desc, value=opt_values[id].split('-'))
                opt_obj = self.option.get(opt_values[id]) # Ключ - строка вариантов опции 'S-M-L'

                if opt_obj is None:
                    self.option[opt_values[id]] = new_opt_obj
                    opt_id=new_opt_obj.id
                else:
                    opt_id=opt_obj.id

                opt_id_list.append(opt_id)

            self.optionvalue.append(OptionValue(product_id=self.product_id, option_id=opt_id_list, obj=opt_list))

            # print('opt_id ' + str(opt_id_list)) ###

    def parse_attribute(self, csv_line):
        """Парснинг атрибутов"""

        multiple_attr_list = csv_line["_ATTRIBUTES_"].split("\n")
        for single_attr_list in multiple_attr_list:
            # Аттрибуты
            if single_attr_list in (''):
                continue

            attr_list = single_attr_list.split("|")
            group_desc = attr_list[0]

            if group_desc in self.attr_group.keys():
                group_id = self.attr_group[group_desc]#.id
            else:
                group_id = len(self.attr_group) + 1
                self.attr_group[group_desc] = group_id#AttributeGroup(id=len(self.attr_group)+1, desc=group_desc)


            self.attribute.append(Attribute(id=len(self.attribute)+1,
                                            desc=attr_list[1],
                                            attr=attr_list[2],
                                            group_id=group_id,
                                            product_id=self.product_id))



    def sql_export(self):
        """Export data to sql"""
        print('-------------sql_export-------------')

        self.oc_attribute = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute`;\n\n' \
            'INSERT INTO `oc_attribute` (`attribute_id`, `attribute_group_id`, `sort_order`) VALUES\n'

        self.oc_attribute_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute_description`;\n\n' \
            'INSERT INTO `oc_attribute_description` (`attribute_id`, `language_id`, `name`) VALUES\n'

        self.oc_attribute_group = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute_group`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute_group`;\n\n' \
            'INSERT INTO `oc_attribute_group` (`attribute_group_id`, `sort_order`) VALUES\n'

        self.oc_attribute_group_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute_group_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute_group_description`;\n\n' \
            'INSERT INTO `oc_attribute_group_description` (`attribute_group_id`, `language_id`, `name`) VALUES\n'

        self.temp_oc_attribute = Template('($attribute_id, $attribute_group_id, 0),\n')
        self.temp_oc_attribute_description = Template('($attribute_id, 1, $name),\n')
        self.temp_oc_attribute_group = Template('($attribute_group_id, 0),\n')
        self.temp_oc_attribute_group_description = Template('($attribute_group_id, 1, $name),\n')






        self.create_attribute_sql()




    def create_attribute_sql(self):
        """Экспорт sql по опциям"""
        for attr in self.attribute:
            # print(attr)

            # self.id = id
            # self.desc = desc
            # self.attr = attr  # oc_product_attribute.text
            # self.group_id = group_id
            # self.product_id = product_id

            self.oc_attribute += self.temp_oc_attribute.substitute({
                'attribute_id': attr.id,
                'attribute_group_id': attr.group_id
            })

            self.oc_attribute_description += self.temp_oc_attribute_description.substitute({
                'attribute_id': attr.id,
                'name': attr.desc
            })


        for group in self.attr_group:
            self.oc_attribute_group += self.temp_oc_attribute_group.substitute({
                'attribute_group_id': self.attr_group[group]
            })

            self.oc_attribute_group_description += self.temp_oc_attribute_group_description.substitute({
                'attribute_group_id': self.attr_group[group],
                'name': group
            })

if __name__ == "__main__":

    csvimport = CSVImport(csv_file, sql_file)
    csvimport.sql_export()

    print(csvimport.oc_attribute)
    print(csvimport.oc_attribute_description)
    print(csvimport.oc_attribute_group)
    print(csvimport.oc_attribute_group_description)

    csvimport.create_attribute_sql()
    csvimport.create_category_sql()
    csvimport.create_manufacturer_sql()
    csvimport.create_option_sql()
    csvimport.create_product_sql()
    csvimport.create_product_option_sql()













