from db_methods import DBMethods

func = DBMethods("postgres","postgres", "123gh45")

func.connect_db()
func.create_init_tables()

func.add_new_client("Ivan", "Ivanov", "ivan@ya.ru")
func.add_new_client("Vasily", "Vasilev", "vasya@ya.ru")
func.add_new_client("Sergey", "Sergeev", "sergey@ya.ru")

func.add_phone_to_client("Ivan", "Ivanov")
func.add_phone_to_client("Vasily", "Vasilev", ["+79151234567"])
func.add_phone_to_client("Sergey", "Sergeev", ["+79099876543","+79251112233","+79075556677"])

func.change_client("Vasily", "Vasilev","vasya@ya.ru", "Maxim",
                   "Maximov","maxim@ya.ru")

func.delete_phone("Sergey", "Sergeev", "sergey@ya.ru", "+79075556677")
func.delete_client("Maxim","Maximov","maxim@ya.ru")

print(func.get_client("Sergey", "Sergeev", "sergey@ya.ru", "+79251112233")[0])


