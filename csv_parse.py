"""
autor: NelsonEAX
http://www.opencartlabs.ru/csv-price-pro-importexport-3/csvprice3-doc-csv/
http://www.opencartlabs.ru/csv-price-pro-importexport-3/import-opencart-options/
"""

import csv
from datetime import datetime
from string import Template

csv_file = 'analyze/opencart_csv-price-pro-importexport-4.csv'
sql_file = 'sql/result_{}.sql'.format(datetime.today().strftime("%Y_%m_%d_%H_%M_%S"))

class Attribute:
    """Атрибуты и связи"""

    def __init__(self, id, desc, group_id):
        """Constructor"""
        self.id = id
        self.desc = desc
        self.group_id = group_id

class AttributeGroup:
    """Группы атрибутов"""

    def __init__(self, id, desc):
        """Constructor"""
        self.id = id
        self.desc = desc

class ProductAttr:
    """Атрибуты продукции"""

    def __init__(self, desc, attr_id, product_id):
        """Constructor"""
        self.desc = desc    # oc_product_attribute.text
        self.attr_id = attr_id
        self.product_id = product_id

class Category:
    """Категории"""

    def __init__(self, name, date, id, parent = 0, path={}):
        """Constructor"""
        self.category_id = id
        self.name = name # obj["_CATEGORY_"]
        self.image = None
        self.parent_id = parent
        self.path = path
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

    def __init__(self, id, obj):
        """Constructor"""
        self.manufacturer_id = id
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

    def __init__(self, id, type, desc ):
        """Constructor"""
        self.id = id
        self.type = type #oc_option radio/checkbox/text/select/textarea/file/date/time/datetime
        self.desc = desc #oc_option_description

class OptionValue:
    """ВариантыОпций"""

    def __init__(self, id, option_id, desc):
        """Constructor"""
        self.id = id
        self.option_id = option_id
        self.desc = desc

class ProductOption:
    """ЗначенияОпций"""

    def __init__(self, product_option_id, product_id, option_id, option_value_id, obj):
        """Constructor"""
        self.product_option_id = product_option_id
        self.product_id = product_id
        self.option_id = option_id
        self.option_value_id = option_value_id
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

    def __init__(self, obj, manufacturer_id):
        """Constructor"""
        self.name = obj["_NAME_"]
        self.model = obj["_MODEL_"]
        self.sku = obj["_SKU_"]
        self.price = obj["_PRICE_"]
        self.quantity = obj["_QUANTITY_"]
        self.description = obj["_DESCRIPTION_"]
        self.weight = obj["_WEIGHT_"] # Вес
        self.length = obj["_LENGTH_"] # Длина
        self.shipping = obj["_SHIPPING_"]
        self.subtract = obj["_subtract_"]
        self.html_h1 = obj["_HTML_H1_"]
        self.html_title = obj["_HTML_TITLE_"]
        self.special = obj["_SPECIAL_"]
        self.image = obj["_IMAGE_"]
        self.manufacturer_id = manufacturer_id
        # Изображения забиваем в словарь. Ключ позже станет сортировкой
        imgs = dict()
        for img in obj["_IMAGES_"].split(','):
            if img in (''):
                continue
            imgs[len(imgs)] = img
        self.images = imgs

class Sql:
    """sql"""
    def __init__(self):
        # attribute---------------------------------------------------------
        self.oc_attribute = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute`;\n' \
            'INSERT INTO `oc_attribute` (`attribute_id`, `attribute_group_id`, `sort_order`) VALUES\n'

        self.oc_attribute_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute_description`;\n' \
            'INSERT INTO `oc_attribute_description` (`attribute_id`, `language_id`, `name`) VALUES\n'

        self.oc_attribute_group = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute_group`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute_group`;\n' \
            'INSERT INTO `oc_attribute_group` (`attribute_group_id`, `sort_order`) VALUES\n'

        self.oc_attribute_group_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_attribute_group_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_attribute_group_description`;\n' \
            'INSERT INTO `oc_attribute_group_description` (`attribute_group_id`, `language_id`, `name`) VALUES\n'

        # category---------------------------------------------------------
        self.oc_category = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_category`\n--\n\n' \
            'TRUNCATE TABLE `oc_category`;\n' \
            'INSERT INTO `oc_category` (`category_id`, `image`, `parent_id`, `top`, `column`, `sort_order`, ' \
            '`status`, `date_added`, `date_modified`) VALUES\n'

        self.oc_category_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_category_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_category_description`;\n' \
            'INSERT INTO `oc_category_description` (`category_id`, `language_id`, `name`, `description`, ' \
            '`meta_title`, `meta_description`, `meta_keyword`) VALUES\n'

        self.oc_category_path = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_category_path`\n--\n\n' \
            'TRUNCATE TABLE `oc_category_path`;\n' \
            'INSERT INTO `oc_category_path` (`category_id`, `path_id`, `level`) VALUES\n'

        self.oc_category_to_layout = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_category_to_layout`\n--\n\n' \
            'TRUNCATE TABLE `oc_category_to_layout`;\n' \
            'INSERT INTO `oc_category_to_layout` (`category_id`, `store_id`, `layout_id`) VALUES\n'

        self.oc_category_to_store = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_category_to_store`\n--\n\n' \
            'TRUNCATE TABLE `oc_category_to_store`;\n' \
            'INSERT INTO `oc_category_to_store` (`category_id`, `store_id`) VALUES\n'

        # manufacturer---------------------------------------------------------
        self.oc_manufacturer = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_manufacturer`\n--\n\n' \
            'TRUNCATE TABLE `oc_manufacturer`;\n' \
            'INSERT INTO `oc_manufacturer` (`manufacturer_id`, `name`, `image`, `sort_order`) VALUES\n'

        self.oc_manufacturer_to_store = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_manufacturer_to_store`\n--\n\n' \
            'TRUNCATE TABLE `oc_manufacturer_to_store`;\n' \
            'INSERT INTO `oc_manufacturer_to_store` (`manufacturer_id`, `store_id`) VALUES\n'

        # option---------------------------------------------------------
        self.oc_option = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_option`\n--\n\n' \
            'TRUNCATE TABLE `oc_option`;\n' \
            'INSERT INTO `oc_option` (`option_id`, `type`, `sort_order`) VALUES\n'

        self.oc_option_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_option_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_option_description`;\n' \
            'INSERT INTO `oc_option_description` (`option_id`, `language_id`, `name`) VALUES\n'

        self.oc_option_value = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_option_value`\n--\n\n' \
            'TRUNCATE TABLE `oc_option_value`;\n' \
            'INSERT INTO `oc_option_value` (`option_value_id`, `option_id`, `image`, `sort_order`) VALUES\n'

        self.oc_option_value_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_option_value_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_option_value_description`;\n' \
            'INSERT INTO `oc_option_value_description` (`option_value_id`, `language_id`, `option_id`, `name`) VALUES\n'

        # product---------------------------------------------------------
        self.oc_product = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product`\n--\n\n' \
            'TRUNCATE TABLE `oc_product`;\n' \
            'INSERT INTO `oc_product` (`product_id`, `model`, `sku`, `upc`, `ean`, `jan`, `isbn`, ' \
            '`mpn`, `location`, `quantity`, `stock_status_id`, `image`, `manufacturer_id`, ' \
            '`shipping`, `price`, `points`, `tax_class_id`, `date_available`, `weight`, ' \
            '`weight_class_id`, `length`, `width`, `height`, `length_class_id`, `subtract`, ' \
            '`minimum`, `sort_order`, `status`, `viewed`, `date_added`, `date_modified`) VALUES\n'

        self.oc_product_attribute = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product_attribute`\n--\n\n' \
            'TRUNCATE TABLE `oc_product_attribute`;\n' \
            'INSERT INTO `oc_product_attribute` (`product_id`, `attribute_id`, `language_id`, `text`) VALUES\n'

        self.oc_product_description = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product_description`\n--\n\n' \
            'TRUNCATE TABLE `oc_product_description`;\n' \
            'INSERT INTO `oc_product_description` (`product_id`, `language_id`, `name`, `description`, `tag`,' \
            ' `meta_title`, `meta_description`, `meta_keyword`) VALUES\n'

        self.oc_product_image = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product_image`\n--\n\n' \
            'TRUNCATE TABLE `oc_product_image`;\n' \
            'INSERT INTO `oc_product_image` (`product_id`, `image`, `sort_order`) VALUES\n'

        self.oc_product_option = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product_option`\n--\n\n' \
            'TRUNCATE TABLE `oc_product_option`;\n' \
            'INSERT INTO `oc_product_option` (`product_option_id`, `product_id`, `option_id`, `value`, `required`) VALUES\n'

        self.oc_product_option_value = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product_option_value`\n--\n\n' \
            'TRUNCATE TABLE `oc_product_option_value`;\n' \
            'INSERT INTO `oc_product_option_value` (`product_option_id`, `product_id`, ' \
            '`option_id`, `option_value_id`, `quantity`, `subtract`, `price`, ' \
            '`price_prefix`, `points`, `points_prefix`, `weight`, `weight_prefix`) VALUES\n'

        self.oc_product_to_layout = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product_to_layout`\n--\n\n' \
            'TRUNCATE TABLE `oc_product_to_layout`;\n' \
            'INSERT INTO `oc_product_to_layout` (`product_id`, `store_id`, `layout_id`) VALUES\n'

        self.oc_product_to_store = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_product_to_store`\n--\n\n' \
            'TRUNCATE TABLE `oc_product_to_store`;\n' \
            'INSERT INTO `oc_product_to_store` (`product_id`, `store_id`) VALUES\n'

        # url_alias---------------------------------------------------------
        self.oc_url_alias = '' \
            '\n\n--\n-- Дамп данных таблицы `oc_url_alias`\n--\n\n' \
            'TRUNCATE TABLE `oc_url_alias`;\n' \
            'INSERT INTO `oc_url_alias` (`url_alias_id`, `query`, `keyword`) VALUES\n'

    def to_str(self):
        self.method_list = [func for func in dir(self) if callable(getattr(self, func))]

class Temp:
    """sql-template"""
    def __init__(self):
        # attribute---------------------------------------------------------
        self.oc_attribute = Template("($attribute_id, $attribute_group_id, 0),\n")
        self.oc_attribute_description = Template("($attribute_id, 1, '$name'),\n")
        self.oc_attribute_group = Template("($attribute_group_id, 0),\n")
        self.oc_attribute_group_description = Template("($attribute_group_id, 1, '$name'),\n")

        # category---------------------------------------------------------
        self.oc_category = Template(
            "($category_id, '', $parent_id, 1, 1, 3, 1, '$date_added', '$date_modified'),\n")
        self.oc_category_description = Template("($category_id, 1, '$name', '$description', '', '', ''),\n")
        self.oc_category_path = Template("($category_id, $path_id, $level),\n")
        self.oc_category_to_layout = Template("($category_id, 0, 0),\n")
        self.oc_category_to_store = Template("($category_id, 0),\n")

        # manufacturer---------------------------------------------------------
        self.oc_manufacturer = Template("($manufacturer_id, '$name', '', 0),\n")
        self.oc_manufacturer_to_store = Template("($manufacturer_id, 0),\n")

        # option---------------------------------------------------------
        self.oc_option = Template("($option_id, '$type', $sort_order),\n")
        self.oc_option_description = Template("($option_id, 1, '$name'),\n")
        self.oc_option_value = Template("($option_value_id, $option_id, '', 0),\n")
        self.oc_option_value_description = Template("($option_value_id, 1, $option_id, '$name'),\n")

        # product---------------------------------------------------------
        self.oc_product = Template("('$product_id', '$model', '$sku', '', '', '', '', '', '$location', "
                                        "$quantity, $stock_status_id, '$image', $manufacturer_id, $shipping, '$price', "
                                        "$points, $tax_class_id, '$date_available', '$weight', $weight_class_id, "
                                        "'$length', '$width', '$height', $length_class_id, $subtract, $minimum, "
                                        "$sort_order, $status, $viewed, '$date_added', '$date_modified'),\n")

        self.oc_product_attribute = Template("($product_id, $attribute_id, 1, '$text'),\n")
        self.oc_product_description = Template("($product_id, 1, '$name', '$description', '$tag', '$meta_title', "
                                                    "'$meta_description', '$meta_keyword'),\n")
        self.oc_product_image = Template("($product_id, '$image', $sort_order),\n")
        self.oc_product_option = Template("($product_option_id, $product_id, $option_id, '$value', 1),\n")
        self.oc_product_option_value = Template("($product_option_id, $product_id, "
                                                     "$option_id, $option_value_id, $quantity, $subtract, "
                                                     "'$price', '$price_prefix', $points, '$points_prefix', "
                                                     "'$weight', '$weight_prefix'),\n")
        self.oc_product_to_layout = Template("($product_id, 0, 0),\n")  # ???
        self.oc_product_to_store = Template("($product_id, 0),\n")

        # url_alias---------------------------------------------------------
        self.oc_url_alias = Template("($url_alias_id, '$query', '$keyword'),\n")  # ???

class CSVImport:
    """Класс генерации sql-файла ипорта прайса от Поставщика Счастья из csv"""

    def __init__(self, csv_file, sql_file):
        """Constructor"""
        self.csv_file = csv_file
        self.sql_file = sql_file
        self.date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        self.sql = Sql()
        self.temp = Temp()

        self.attribute = dict()
        self.attr_group = dict()
        self.category = dict()
        self.categories_id = set()
        self.manufacturer = dict()
        self.option = dict()
        self.optionvalue = list()
        self.product = set()
        self.prodattr = set()
        self.prodoption = list()
        self.product_id = None # Текущий товар, его id у поставщика
        self.manufacturer_id = None # Текущий id поставщика

        with open(self.csv_file, 'r', encoding='utf-8') as f_obj:
            self.csv_reader(f_obj)

    def csv_reader(self, file_obj):
        """
        Read a CSV file using csv.DictReader
        """
        print('-------------csv_reader-------------' + datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
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
        self.product.add(Product(csv_line, self.manufacturer_id))
        self.product_id = csv_line["_SKU_"]

    def parse_manufacturer(self, csv_line):
        """Парсинг производителей"""
        desc = csv_line["_MANUFACTURER_"]
        if desc in self.manufacturer.keys():
            self.manufacturer_id = self.manufacturer[desc].manufacturer_id
        else:
            self.manufacturer_id = len(self.manufacturer) + 1
            self.manufacturer[desc] = Manufacturer(id=self.manufacturer_id, obj=csv_line)

    def parse_category(self, csv_line):
        """Парсинг категорий"""
        # Несколько категорий
        self.categories_id.clear()
        multiple_cat_list = csv_line["_CATEGORY_"].split("\n")
        for single_cat_list in multiple_cat_list:
            # Категории
            parent = 0
            path = {}
            cat_list = single_cat_list.split("|")

            for category in cat_list:
                path[len(path)] = parent# (len(self.category) + 1) if parent == 0 else parent
                new_cat_obj = Category(name=category, date=self.date, id=len(self.category) + 1, parent=parent, path=path)

                cat_obj = self.category.get(category)
                if cat_obj is None:
                    self.category[category] = new_cat_obj
                    parent = new_cat_obj.category_id
                    path[len(path)] = parent
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
            opt_value_id_list = list() # лист id значений опций текущего товара

            for id, opt_desc in enumerate(opt_descs):

                if id > len(opt_values)-1:
                    continue

                new_opt_obj = Option(id=len(self.option) + 1, type=opt_type, desc=opt_desc)
                opt_obj = self.option.get(opt_values[id]) # Ключ - строка вариантов опции 'S-M-L'

                if opt_obj is None:
                    self.option[opt_values[id]] = new_opt_obj
                    opt_id=new_opt_obj.id
                    # Варианты опций
                    values = opt_values[id].split('-')
                    for value in values:
                        new_opt_value_id = len(self.optionvalue) + 1
                        opt_value_id_list.append(new_opt_value_id)
                        self.optionvalue.append(OptionValue(id=new_opt_value_id, option_id=opt_id, desc=value))
                else:
                    opt_id=opt_obj.id
                    for item in self.optionvalue:
                        if item.option_id == opt_obj.id:
                            opt_value_id_list.append(item.id)

                # Связи с продукцией
                opt_id_list.append(opt_id)

            for _opt_id in opt_id_list:
                for _opt_value_id in opt_value_id_list:
                    self.prodoption.append(ProductOption(product_option_id = len(self.prodoption)+1,
                                                         product_id=self.product_id,
                                                         option_id=_opt_id,
                                                         option_value_id=_opt_value_id,
                                                         obj=opt_list))
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
            attr_desc = attr_list[1]

            if group_desc in self.attr_group.keys():
                group_id = self.attr_group[group_desc]#.id
            else:
                group_id = len(self.attr_group) + 1
                self.attr_group[group_desc] = group_id#AttributeGroup(id=len(self.attr_group)+1, desc=group_desc)

            if attr_desc in self.attribute.keys():
                attr_id = self.attribute[attr_desc].id
            else:
                attr_id = len(self.attribute) + 1
                self.attribute[attr_desc] = Attribute(id=attr_id,
                                                      desc=attr_desc,
                                                      group_id=group_id)

            self.prodattr.add(ProductAttr(desc=attr_list[2],
                                         attr_id=attr_id,
                                         product_id=self.product_id))

    def sql_export_to_file(self):
        """Export sql data to file"""
        print('--------sql_export_to_file----------' + datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

        def methods(cls):
            return [x for x, y in cls.__dict__.items()]

        sql_objs = methods(self.sql)

        with open(self.sql_file, 'w+', encoding='utf-8') as f_sql_obj:
            for sql_obj in sql_objs:
                sql = getattr(self.sql, sql_obj)
                sql = sql[:-2] + ';'
                f_sql_obj.write(sql)

    def sql_export(self):
        """Export data to sql"""
        print('-------------sql_export-------------' + datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

        # self.create_attribute_sql()
        self.create_category_sql()
        # self.create_manufacturer_sql()
        # self.create_option_sql()
        # self.create_product_sql()

        self.sql_export_to_file()

    def create_attribute_sql(self):
        """Экспорт sql по атрибутам"""
        for desc in self.attribute:
            attr = self.attribute[desc]

            self.sql.oc_attribute += self.temp.oc_attribute.substitute({
                'attribute_id': attr.id,
                'attribute_group_id': attr.group_id
            })

            self.sql.oc_attribute_description += self.temp.oc_attribute_description.substitute({
                'attribute_id': attr.id,
                'name': attr.desc
            })

        for group in self.attr_group:
            self.sql.oc_attribute_group += self.temp.oc_attribute_group.substitute({
                'attribute_group_id': self.attr_group[group]
            })

            self.sql.oc_attribute_group_description += self.temp.oc_attribute_group_description.substitute({
                'attribute_group_id': self.attr_group[group],
                'name': group
            })

    def create_category_sql(self):
        """Экспорт sql по категориям"""
        for key in self.category:
            item = self.category[key]

            self.sql.oc_category += self.temp.oc_category.substitute({
                'category_id': item.category_id,
                'parent_id': item.parent_id,
                'date_added': item.date_added,
                'date_modified': item.date_modified
            })

            self.sql.oc_category_description += self.temp.oc_category_description.substitute({
                'category_id': item.category_id,
                'name': item.name,
                'description': ''
            })

            for level in item.path:
                self.sql.oc_category_path += self.temp.oc_category_path.substitute({
                    'category_id': item.category_id,
                    'path_id': item.path[level],
                    'level': level
                })

            self.sql.oc_category_to_layout += self.temp.oc_category_to_layout.substitute({
                'category_id': item.category_id
            })

            self.sql.oc_category_to_store += self.temp.oc_category_to_store.substitute({
                'category_id': item.category_id
            })

    def create_manufacturer_sql(self):
        """Экспорт sql по производители"""
        def get_id(key):
            """Для сортировки сет по id"""
            return self.manufacturer[key].manufacturer_id

        for key in sorted(self.manufacturer, key=get_id):
            item = self.manufacturer[key]
            self.sql.oc_manufacturer += self.temp.oc_manufacturer.substitute({
                'manufacturer_id': item.manufacturer_id,
                'name': item.name
            })
            self.sql.oc_manufacturer_to_store += self.temp.oc_manufacturer_to_store.substitute({
                'manufacturer_id': item.manufacturer_id
            })

    def create_option_sql(self):
        """Экспорт sql по опции"""
        for key in self.option:
            item = self.option[key]
            self.sql.oc_option += self.temp.oc_option.substitute({
                'option_id': item.id,
                'type': item.type,
                'sort_order': item.id
            })
            self.sql.oc_option_description += self.temp.oc_option_description.substitute({
                'option_id': item.id,
                'name': item.desc
            })

        def get_id(item):
            """Для сортировки листа по id"""
            return item.id

        for item in sorted(self.optionvalue, key=get_id):
            self.sql.oc_option_value += self.temp.oc_option_value.substitute({
                'option_value_id': item.id,
                'option_id': item.option_id
            })
            self.sql.oc_option_value_description += self.temp.oc_option_value_description.substitute({
                'option_value_id': item.id,
                'option_id': item.option_id,
                'name': item.desc
            })

    def create_product_sql(self):
        """Экспорт sql по продукция"""
        # for item in self.product:
        #     self.sql.oc_product += self.temp.oc_product.substitute({
        #         'product_id': item.sku,
        #         'model': item.model,
        #         'sku': item.sku,
        #         'location': '',
        #         'quantity': item.quantity,
        #         'stock_status_id': 7, # oc_stock_status 7, 'В наличии'
        #         'image': item.image,
        #         'manufacturer_id': item.manufacturer_id,
        #         'shipping': item.shipping,
        #         'price': item.price,
        #         'points': 0,
        #         'tax_class_id': 9, # oc_tax_class 9, 'Налоги', 'Облагаемые налогом'
        #         'date_available': self.date,
        #         'weight': '0.00000000' if item.weight == '' else item.weight,
        #         'weight_class_id': 2,# oc_weight_class_description (2, 1, 'Грамм', 'г');
        #         'length': '0.00000000' if item.length == '' else item.length,
        #         'width': '0.00000000',
        #         'height': '0.00000000',
        #         'length_class_id': 2, # oc_length_class_description (2, 1, 'Миллиметр', 'мм');
        #         'subtract': item.subtract,
        #         'minimum': 1,
        #         'sort_order': 1,
        #         'status': 1,
        #         'viewed': 0,
        #         'date_added': self.date,
        #         'date_modified': self.date
        #     })
        #
        #     self.sql.oc_product_description += self.temp.oc_product_description.substitute({
        #         'product_id': item.sku,
        #         'name': item.name,
        #         'description': item.description,
        #         'tag': '',
        #         'meta_title': item.html_title,
        #         'meta_description': item.html_h1,
        #         'meta_keyword': item.html_h1
        #     })
        #
        #     for key in item.images:
        #         image = item.image[key]
        #         self.sql.oc_product_image += self.temp.oc_product_image.substitute({
        #             'product_id': item.sku,
        #             'image': image,
        #             'sort_order': 0
        #         })
        #
        #     self.sql.oc_product_to_layout += self.temp.oc_product_to_layout.substitute({
        #         'product_id': item.sku
        #     })
        #     self.sql.oc_product_to_store += self.temp.oc_product_to_store.substitute({
        #         'product_id': item.sku
        #     })
        #
        # for item in self.prodattr:
        #     self.sql.oc_product_attribute += self.temp.oc_product_attribute.substitute({
        #         'product_id': item.product_id,
        #         'attribute_id': item.attr_id,
        #         'text': item.desc
        #     })

        for item in self.prodoption:
            self.sql.oc_product_option += self.temp.oc_product_option.substitute({
                'product_option_id': item.product_option_id,
                'product_id': item.product_id,
                'option_id': item.option_id,
                'value': ''
            })

            self.sql.oc_product_option_value += self.temp.oc_product_option_value.substitute({
                # 'product_option_value_id': item.product_option_id,
                'product_option_id': item.product_option_id,
                'product_id': item.product_id,
                'option_id': item.option_id,
                'option_value_id': item.option_value_id,
                'quantity': item.quantity,
                'subtract': item.subtract,
                'price': item.price,
                'price_prefix': item.price_prefix,
                'points': item.points,
                'points_prefix': item.points_prefix,
                'weight': item.weight,
                'weight_prefix': item.weight_prefix
            })

if __name__ == "__main__":

    csvimport = CSVImport(csv_file, sql_file)
    csvimport.sql_export()

    # print(csvimport.sql.oc_attribute)
    # print(csvimport.sql.oc_attribute_description)
    # print(csvimport.sql.oc_attribute_group)
    # print(csvimport.sql.oc_attribute_group_description)
    # print(csvimport.sql.oc_category)
    # print(csvimport.sql.oc_category_description)
    # print(csvimport.sql.oc_category_path)
    # print(csvimport.sql.oc_category_to_layout)
    # print(csvimport.sql.oc_category_to_store)
    # print(csvimport.sql.oc_manufacturer)
    # print(csvimport.sql.oc_manufacturer_to_store)
    # print(csvimport.sql.oc_option)
    # print(csvimport.sql.oc_option_description)
    # print(csvimport.sql.oc_option_value)
    # print(csvimport.sql.oc_option_value_description)

    # print(csvimport.sql.oc_product)
    # print(csvimport.sql.oc_product_attribute)
    # print(csvimport.sql.oc_product_description)
    # print(csvimport.sql.oc_product_image)
    # print(csvimport.sql.oc_product_option)
    # print(csvimport.sql.oc_product_option_value)
    # print(csvimport.sql.oc_product_to_layout)
    # print(csvimport.sql.oc_product_to_store)

















