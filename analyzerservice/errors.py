class Missing(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)  # Вызываем родительский конструктор
        self.msg = msg

    def __str__(self) -> str:
        return f"Missing: {self.msg}"  # Переопределяем метод для вывода сообщения
